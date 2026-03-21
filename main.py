"""メインオーケストレーション

完成サイトを GitHub に push し Vercel で公開するまでを一本化する。

パイプライン概略:
  1. ヒアリングシート類の抽出（`modules.case_extraction`）
  2. TEXT_LLM（`modules.text_llm_stage` — プラン別 Gemini マニュアルまたは `llm_mock`）
  3. サイト土台生成 → `llm_raw_output/` に LLM 生出力を保存
  4. フェンス解析で `app/` 等へ反映（失敗時は例外）
  5. `GEMINI_API_KEY` 利用時: Gemini 画像 API で `ImagePlaceholder` を実ファイル化
  6. ビルド検証 → GitHub push → Vercel デプロイ → スプレッドシートに公開 URL

各段の LLM 割当は ``docs/LLM_PIPELINE.md`` を参照。
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
    BOT_MAX_CASES,
    GEMINI_API_KEY,
    GEMINI_SITE_IMAGE_DELAY_SEC,
    GEMINI_SITE_IMAGE_MAX_SLOTS,
    GEMINI_SITE_IMAGE_MODEL,
    SITE_BUILD_ENABLED,
    SITE_IMPLEMENTATION_ENABLED,
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN,
    SPREADSHEET_HEADERS_STRICT,
    get_contract_plan_info,
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
from modules.basic_lp_generated_apply import apply_contract_outputs_to_site_dir
from modules.case_extraction import extract_hearing_bundle
from modules.contract_workflow import (
    ContractWorkBranch,
    gemini_manual_enabled_for_branch,
    resolve_contract_work_branch,
)
from modules.github_client import GitHubClient, sanitize_github_repo_name
from modules.llm_raw_output import write_llm_raw_artifacts
from modules.site_build import verify_site_build_with_cursor_pass
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
        " modules.basic_lp_text_llm",
        "（modules.basic_lp_text_llm）。",
        " modules.basic_text_llm",
        "（modules.basic_text_llm）。",
        " modules.basic_lp_gemini_manual",
        "（modules.basic_lp_gemini_manual）。",
        " modules.basic_cp_gemini_manual",
        "（modules.basic_cp_gemini_manual）。",
        " modules.standard_cp_gemini_manual",
        "（modules.standard_cp_gemini_manual）。",
        " modules.advance_cp_gemini_manual",
        "（modules.advance_cp_gemini_manual）。",
        " modules.standard_text_llm",
        "（modules.standard_text_llm）。",
        " modules.advance_text_llm",
        "（modules.advance_text_llm）。",
        " modules.basic_lp_generated_apply",
        "（modules.basic_lp_generated_apply）。",
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
        self.vercel_client = VercelClient()

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
            if not (hearing_bundle.hearing_sheet_content or "").strip():
                logger.warning(
                    "ヒアリング本文が空のため案件をスキップします row=%s record=%s partner=%s",
                    case.get("row_number"),
                    case.get("record_number"),
                    case.get("partner_name"),
                )
                self.spreadsheet.update_ai_status(
                    case["row_number"],
                    "スキップ: ヒアリング本文なし（AH列の取得結果が空）",
                )
                return None

            plan_raw = (case.get("contract_plan") or "").strip()
            plan_info = get_contract_plan_info(plan_raw)
            work_branch = resolve_contract_work_branch(case["contract_plan"])
            if work_branch == ContractWorkBranch.BASIC:
                lp_flag = self.spreadsheet.lookup_basic_is_landing_page(
                    str(case.get("record_number") or ""),
                    str(case.get("partner_name") or ""),
                )
                if lp_flag is True:
                    work_branch = ContractWorkBranch.BASIC_LP
                    logger.info(
                        "BASIC サイトタイプシートにより作業分岐を BASIC LP に変更しました "
                        "(record=%r)",
                        case.get("record_number"),
                    )
            logger.info(
                "契約プラン作業分岐: plan=%r branch=%s resolved_type=%s pages=%s",
                plan_raw,
                work_branch.value,
                plan_info.get("type"),
                plan_info.get("pages"),
            )

            if work_branch == ContractWorkBranch.BASIC_LP:
                logger.info(
                    "【フェーズ2】TEXT_LLM（BASIC LP・1ページランディング）… "
                    "modules.basic_lp_text_llm"
                )
            elif work_branch == ContractWorkBranch.BASIC:
                logger.info(
                    "【フェーズ2】TEXT_LLM（BASIC・コーポレート1ページ）… "
                    "modules.basic_text_llm（現状モック）"
                )
            elif work_branch == ContractWorkBranch.STANDARD:
                logger.info(
                    "【フェーズ2】TEXT_LLM（STANDARD・コーポレート複数ページ）… "
                    "modules.standard_text_llm"
                )
            elif work_branch == ContractWorkBranch.ADVANCE:
                logger.info(
                    "【フェーズ2】TEXT_LLM（ADVANCE・コーポレート12ページ想定）… "
                    "modules.advance_text_llm"
                )
            else:
                logger.info(
                    "【フェーズ2】TEXT_LLM 処理（要望・仕様）… 現状モック — 実LLMは modules.text_llm_stage を拡張"
                )
            requirements_result, spec = run_text_llm_stage(
                hearing_bundle,
                contract_plan=case["contract_plan"],
                partner_name=case["partner_name"],
                work_branch=work_branch,
            )

            logger.info(
                "【フェーズ3】土台生成・LLM 正本の保存・検証・Git push / デプロイ…"
            )
            logger.info("› Next.js の技術土台を生成…")
            site_name = f"{case['partner_name']}-{case['record_number']}"
            site_dir = self.site_generator.generate_site(spec, [], site_name)

            raw_n = write_llm_raw_artifacts(
                site_dir,
                spec=spec,
                requirements_result=requirements_result,
                work_branch=work_branch,
            )
            logger.info(
                "› LLM 正本: llm_raw_output/ に %s ファイル（形式を強制せずそのまま保存・必ず push）",
                raw_n,
            )

            n_gen = apply_contract_outputs_to_site_dir(
                spec, site_dir, work_branch=work_branch
            )
            if n_gen:
                logger.info(
                    "› フェンス解析でサイトに %s ファイル反映（分岐 %s）",
                    n_gen,
                    work_branch.value,
                )
            if (
                work_branch
                in (
                    ContractWorkBranch.BASIC_LP,
                    ContractWorkBranch.BASIC,
                    ContractWorkBranch.STANDARD,
                    ContractWorkBranch.ADVANCE,
                )
                and n_gen == 0
                and gemini_manual_enabled_for_branch(work_branch)
            ):
                raise RuntimeError(
                    "生成マークダウンからサイトファイルを1件も適用できませんでした。"
                    " 該当プランの Gemini マニュアルとリファクタ出力が spec に入っているか確認してください。"
                )

            if (GEMINI_API_KEY or "").strip():
                from modules.gemini_site_images import materialize_site_images

                n_img = materialize_site_images(
                    site_dir,
                    api_key=GEMINI_API_KEY.strip(),
                    model=GEMINI_SITE_IMAGE_MODEL,
                    max_slots=GEMINI_SITE_IMAGE_MAX_SLOTS,
                    delay_sec_between_calls=GEMINI_SITE_IMAGE_DELAY_SEC,
                )
                if n_img:
                    logger.info(
                        "› Gemini 画像 API: %s 箇所を public/images/generated/ に保存し next/image に置換",
                        n_img,
                    )

            if SITE_IMPLEMENTATION_ENABLED:
                logger.info("› サイト実装を実行（モック: テンプレ土台のビルド検証）…")
                ok_impl, impl_log = self.site_implementer.implement(
                    spec,
                    site_dir,
                    case["contract_plan"],
                    work_branch=work_branch,
                )
                if not ok_impl:
                    raise RuntimeError(
                        "サイト実装または npm build に失敗しました。ログ末尾: "
                        + (impl_log[-2000:] if impl_log else "")
                    )
            elif SITE_BUILD_ENABLED:
                logger.info("› 実装はスキップ — npm build で検証のみ…")
                ok_b, blog = verify_site_build_with_cursor_pass(site_dir)
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
                "test",
            )

            repo_https = github_url.rstrip("/").removesuffix(".git")

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
                try:
                    self.process_case(case)
                except Exception as e:
                    # process_case 内で既に exc_info 付きログ済みのため、ここは要約のみ
                    logger.error(
                        "案件が失敗しましたがバッチは続行します row=%s record=%s: %s",
                        case.get("row_number"),
                        case.get("record_number"),
                        e,
                    )

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
