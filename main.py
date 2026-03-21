"""メインオーケストレーション

パイプライン概略:
  1. ヒアリングシート類の抽出（`modules.case_extraction`）
  2. TEXT_LLM（要望・仕様。実装は `modules.text_llm_stage`、現状モックは `modules.llm_mock`）
  3. サイト生成・検証・GitHub へソース push・（任意）Vercel
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from config.logging_setup import configure_logging

configure_logging()

from config.config import (
    BOT_DEPLOY_URL_SOURCE,
    BOT_MAX_CASES,
    SITE_BUILD_ENABLED,
    SITE_IMPLEMENTATION_ENABLED,
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN,
    SPREADSHEET_HEADERS_STRICT,
)
from config.log_theme import (
    all_done_banner,
    batch_start_banner,
    case_start_banner,
    idle_banner,
    startup_title,
    stream_supports_color,
)
from config.types import CaseRecord
from config.validation import validate_startup_config
from modules.case_extraction import extract_hearing_bundle
from modules.github_client import GitHubClient, sanitize_github_repo_name
from modules.site_build import verify_site_build
from modules.site_generator import SiteGenerator
from modules.site_implementer import SiteImplementer
from modules.spec_generator import SpecGenerator
from modules.spreadsheet import SpreadsheetClient, missing_required_case_fields
from modules.text_llm_stage import run_text_llm_stage
from modules.vercel_client import VercelClient

logger = logging.getLogger(__name__)


def _format_ai_status_error(exc: BaseException) -> str:
    """AV 列向けに例外メッセージを短く整形（モジュールパス連呼を削る）。"""
    msg = (str(exc) or type(exc).__name__).strip()
    for noise in (
        "（modules.spec_generator.generate_spec）。",
        "（modules.spec_generator）。",
        " modules.spec_generator",
        " modules.llm_mock",
        "（modules.llm_mock）。",
        "（modules.llm_mock.finalize_plain_prompt）。",
        "（modules.llm_mock.build_spec_dict_mock）。",
        " modules.text_llm_stage",
        "（modules.text_llm_stage）。",
        " modules.case_extraction",
        "（modules.case_extraction）。",
    ):
        msg = msg.replace(noise, "")
    msg = " ".join(msg.split())
    prefix = "エラー: "
    budget = max(24, SPREADSHEET_AI_STATUS_ERROR_MAX_LEN - len(prefix))
    if len(msg) > budget:
        msg = msg[: budget - 1] + "…"
    return prefix + msg


class WebsiteBot:
    """Webサイト製作自動化Bot"""

    def __init__(self) -> None:
        """SpreadsheetClient を常に初期化する。"""
        self.spreadsheet = SpreadsheetClient()
        self.spec_generator = SpecGenerator()
        self.site_implementer = SiteImplementer()
        self.site_generator = SiteGenerator()
        self._github_client: GitHubClient | None = None
        # Vercel は BOT_DEPLOY_URL_SOURCE=vercel のときのみ必須
        self.vercel_client: VercelClient | None
        if BOT_DEPLOY_URL_SOURCE == "vercel":
            self.vercel_client = VercelClient()
        else:
            self.vercel_client = None

    @property
    def github_client(self) -> GitHubClient:
        """GitHub push 直前まで初期化しない（起動時の設定検証を軽くする）。"""
        if self._github_client is None:
            self._github_client = GitHubClient()
        return self._github_client

    def process_case(self, case: CaseRecord) -> str | None:
        """
        案件を処理

        Returns:
            デプロイURL（成功時）。必須項目不足で着手しない場合のみ None。
            処理中の失敗は AV 列更新後に例外を再送出し、`run()` のバッチはそこで中断される。
        """
        requirements_result: dict[str, Any] | None = None
        spec: dict[str, Any] | None = None
        site_dir: Path | None = None
        impl_log = ""

        try:
            missing = missing_required_case_fields(case)
            if missing:
                logger.error(
                    "必須項目が未入力のため案件に着手しません row=%s missing=%s",
                    case.get("row_number"),
                    missing,
                )
                return None

            _tty_color = stream_supports_color(sys.stdout)
            logger.info(
                case_start_banner(
                    row=case.get("row_number"),
                    record=case.get("record_number"),
                    partner=case.get("partner_name"),
                    use_color=_tty_color,
                )
            )

            self.spreadsheet.update_ai_status(case["row_number"], "処理中")

            logger.info("【フェーズ1】ヒアリングシート類の抽出…")
            hearing_bundle = extract_hearing_bundle(
                case,
                fetch_hearing_sheet=self.spec_generator.fetch_hearing_sheet,
            )

            logger.info(
                "【フェーズ2】TEXT_LLM 処理（要望・仕様）… 現状モック — 実LLMは modules.text_llm_stage を拡張"
            )
            requirements_result, spec = run_text_llm_stage(
                hearing_bundle,
                contract_plan=case["contract_plan"],
                partner_name=case["partner_name"],
            )

            logger.info(
                "【フェーズ3】サイト生成・ビルド検証・ソースコード push / デプロイ…"
            )
            logger.info("› Next.js の技術土台を生成…")
            site_name = f"{case['partner_name']}-{case['record_number']}"
            site_dir = self.site_generator.generate_site(spec, [], site_name)

            if SITE_IMPLEMENTATION_ENABLED:
                logger.info("› サイト実装を実行（モック: テンプレ土台のビルド検証）…")
                ok_impl, impl_log = self.site_implementer.implement(
                    spec,
                    site_dir,
                    case["contract_plan"],
                )
                if not ok_impl:
                    raise RuntimeError(
                        "サイト実装または npm build に失敗しました。ログ末尾: "
                        + (impl_log[-2000:] if impl_log else "")
                    )
            elif SITE_BUILD_ENABLED:
                logger.info("› 実装はスキップ — npm build で検証のみ…")
                ok_b, blog = verify_site_build(site_dir)
                blog = blog or ""
                if not ok_b:
                    raise RuntimeError(
                        "npm build に失敗: " + (blog[-2000:] if blog else "")
                    )

            logger.info("› GitHub にソースコードを push…")
            repo_name = sanitize_github_repo_name(
                case["partner_name"], str(case["record_number"])
            )
            github_url = self.github_client.push_to_github(
                site_dir,
                repo_name,
                f"{case['partner_name']}のWebサイト",
            )

            if BOT_DEPLOY_URL_SOURCE == "github":
                deploy_url = github_url.rstrip("/").removesuffix(".git")
                logger.warning(
                    "BOT_DEPLOY_URL_SOURCE=github のため Vercel をスキップし、"
                    "GitHub リポジトリ URL をデプロイ列に記録します: %s",
                    deploy_url,
                )
            else:
                if self.vercel_client is None:
                    raise RuntimeError(
                        "VercelClient が未初期化です（BOT_DEPLOY_URL_SOURCE=vercel を確認）"
                    )
                logger.info("› Vercel にデプロイ…")
                deployment = self.vercel_client.deploy_from_github(
                    github_url, repo_name
                )
                deploy_url = deployment["url"]

                logger.info("› デプロイ URL が開けるか確認…")
                if not self.vercel_client.verify_deployment_url(deploy_url):
                    logger.warning("デプロイURLが閲覧できません: %s", deploy_url)

            logger.info("› スプレッドシートを更新…")
            self.spreadsheet.update_deploy_url(case["row_number"], deploy_url)

            self.spreadsheet.update_ai_status(case["row_number"], "完了")

            logger.info("✓ 案件完了 — 公開 URL: %s", deploy_url)
            return deploy_url

        except Exception as e:
            logger.error(
                "案件処理エラー row=%s record=%s partner=%s: %s",
                case.get("row_number"),
                case.get("record_number"),
                case.get("partner_name"),
                e,
                exc_info=True,
            )
            try:
                self.spreadsheet.update_ai_status(
                    case["row_number"],
                    _format_ai_status_error(e),
                )
            except Exception as sheet_err:
                logger.warning(
                    "エラー後のスプレッドシートステータス更新に失敗 row=%s: %s",
                    case.get("row_number"),
                    sheet_err,
                    exc_info=True,
                )
            raise

    def run(self) -> None:
        """メイン処理を実行"""
        try:
            _uc = stream_supports_color(sys.stdout)
            logger.info(startup_title(use_color=_uc))

            cases = self.spreadsheet.get_pending_cases()

            if not cases:
                logger.info(idle_banner(use_color=_uc))
                return

            if BOT_MAX_CASES:
                cases = cases[:BOT_MAX_CASES]

            logger.info(
                batch_start_banner(
                    count=len(cases),
                    max_cases=BOT_MAX_CASES or None,
                    use_color=_uc,
                )
            )

            for case in cases:
                self.process_case(case)

            logger.info(all_done_banner(use_color=_uc))

        except Exception as e:
            logger.error("Bot実行エラー: %s", e, exc_info=True)
            raise


def _run_startup_validation() -> bool:
    """検証結果をログに出し、成功なら True"""
    result = validate_startup_config(require_full_pipeline=True)
    for w in result.warnings:
        logger.warning("[設定] %s", w)
    if not result.ok:
        for err in result.errors:
            logger.error("[設定] %s", err)
        return False
    return True


def main() -> None:
    """メイン関数"""
    if os.getenv("BOT_CONFIG_CHECK", "").strip().lower() in ("1", "true", "yes"):
        logging.getLogger().setLevel(logging.INFO)
        result = validate_startup_config(require_full_pipeline=True)
        for w in result.warnings:
            print(f"WARN: {w}")
        for err in result.errors:
            print(f"ERROR: {err}")
        if not result.ok:
            sys.exit(1)
        try:
            from modules.spreadsheet import SpreadsheetClient

            sp = SpreadsheetClient()
            mm = sp.validate_header_labels()
            for m in mm:
                print(f"HEADER_MISMATCH: {m}")
            if SPREADSHEET_HEADERS_STRICT and mm:
                print(
                    "ERROR: 列見出し不一致のため終了（SPREADSHEET_HEADERS_STRICT=true。"
                    " AV・AW は検証対象外）"
                )
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: スプレッドシート列検証で例外: {e}")
            sys.exit(1)
        print("OK: 設定・列見出し検証に問題ありません。")
        sys.exit(0)

    if not _run_startup_validation():
        sys.exit(1)

    try:
        if BOT_DEPLOY_URL_SOURCE == "github":
            logger.warning(
                "BOT_DEPLOY_URL_SOURCE=github — 本番の公開 URL は Vercel ではなく GitHub のみ記録されます"
            )
        bot = WebsiteBot()
        header_issues = bot.spreadsheet.validate_header_labels()
        for msg in header_issues:
            if SPREADSHEET_HEADERS_STRICT:
                logger.error("[起動時・列見出し] %s", msg)
            else:
                logger.warning("[起動時・列見出し] %s", msg)
        if SPREADSHEET_HEADERS_STRICT and header_issues:
            logger.error(
                "列見出し不一致のため起動を中止します。"
                "config.py の SPREADSHEET_HEADER_LABELS をシート1行目に合わせるか（AV・AW は検証対象外）、"
                "SPREADSHEET_HEADERS_STRICT=false で警告のみにしてください。"
            )
            sys.exit(1)
        bot.run()
    except KeyboardInterrupt:
        logger.info("Botを停止しました")
    except Exception as e:
        logger.error("予期しないエラー: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
