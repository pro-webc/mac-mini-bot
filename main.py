"""メインオーケストレーション"""
from __future__ import annotations

import logging
import os
import sys

from config.logging_setup import configure_logging

configure_logging()

from config.config import (
    BOT_DEPLOY_URL_SOURCE,
    BOT_MAX_CASES,
    SITE_BUILD_ENABLED,
    SITE_IMPLEMENTATION_ENABLED,
    SPREADSHEET_HEADERS_STRICT,
)
from config.types import CaseRecord
from config.validation import validate_startup_config
from modules.github_client import GitHubClient, sanitize_github_repo_name
from modules.image_generator import ImageGenerator
from modules.requirement_extractor import RequirementExtractor
from modules.site_build import verify_site_build
from modules.site_generator import SiteGenerator
from modules.site_implementer import SiteImplementer
from modules.spec_generator import SpecGenerator
from modules.spreadsheet import SpreadsheetClient, missing_required_case_fields
from modules.vercel_client import VercelClient

logger = logging.getLogger(__name__)


class WebsiteBot:
    """Webサイト製作自動化Bot"""

    def __init__(self) -> None:
        self.spreadsheet = SpreadsheetClient()
        self.requirement_extractor = RequirementExtractor()
        self.spec_generator = SpecGenerator()
        self.image_generator = ImageGenerator()
        self.site_implementer = SiteImplementer()
        self.site_generator = SiteGenerator()
        self.github_client = GitHubClient()
        # Vercel は BOT_DEPLOY_URL_SOURCE=vercel のときのみ必須
        self.vercel_client: VercelClient | None
        if BOT_DEPLOY_URL_SOURCE == "vercel":
            self.vercel_client = VercelClient()
        else:
            self.vercel_client = None

    def process_case(self, case: CaseRecord) -> str | None:
        """
        案件を処理

        Args:
            case: 案件情報

        Returns:
            デプロイURL（成功時）
        """
        try:
            missing = missing_required_case_fields(case)
            if missing:
                logger.error(
                    "必須項目が未入力のため案件に着手しません row=%s missing=%s",
                    case.get("row_number"),
                    missing,
                )
                return None

            logger.info(
                "案件処理を開始: row=%s record=%s partner=%s",
                case.get("row_number"),
                case.get("record_number"),
                case.get("partner_name"),
            )

            self.spreadsheet.update_ai_status(case["row_number"], "処理中")

            logger.info("ヒアリングシートを取得中...")
            hearing_sheet_content = ""
            if case.get("hearing_sheet_url"):
                hearing_sheet_content = (
                    self.spec_generator.fetch_hearing_sheet(case["hearing_sheet_url"]) or ""
                )

            logger.info("要望を抽出中...")
            requirements_result = self.requirement_extractor.extract_requirements(
                hearing_sheet_content,
                case.get("appo_memo", ""),
                case.get("sales_notes", ""),
                case["contract_plan"],
            )

            logger.info("仕様書を生成中...")
            spec = self.spec_generator.generate_spec(
                hearing_sheet_content,
                requirements_result,
                case["contract_plan"],
                case["partner_name"],
            )

            logger.info("Next.js 技術土台を生成中...")
            site_name = f"{case['partner_name']}-{case['record_number']}"
            site_dir = self.site_generator.generate_site(spec, [], site_name)

            if SITE_IMPLEMENTATION_ENABLED:
                logger.info("サイト実装（LLM）を実行中...")
                if not self.site_implementer.is_configured():
                    raise RuntimeError(
                        "サイト実装用 LLM が未設定です。"
                        "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND（TEXT_LLM_PROVIDER）を設定するか、"
                        "SITE_IMPLEMENTATION_ENABLED=false でスタブのみ運用してください。"
                    )
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
                logger.info("実装スキップのためビルド検証のみ実行...")
                ok_b, blog = verify_site_build(site_dir)
                if not ok_b:
                    raise RuntimeError("npm build に失敗: " + (blog[-2000:] if blog else ""))

            if self.image_generator.is_enabled():
                logger.info("画像パイプライン（分離コンテキスト）を実行中...")
                self.image_generator.generate_after_site(spec, site_dir)
                if SITE_BUILD_ENABLED:
                    ok_img_b, _ = verify_site_build(site_dir, skip_install=True)
                    if not ok_img_b:
                        logger.warning(
                            "画像追加後のビルド検証に失敗しましたが続行します（静的ファイルのみの場合は稀）"
                        )

            logger.info("GitHubにプッシュ中...")
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
                    raise RuntimeError("VercelClient が未初期化です（BOT_DEPLOY_URL_SOURCE=vercel を確認）")
                logger.info("Vercelにデプロイ中...")
                deployment = self.vercel_client.deploy_from_github(github_url, repo_name)
                deploy_url = deployment["url"]

                logger.info("デプロイURLを確認中...")
                if not self.vercel_client.verify_deployment_url(deploy_url):
                    logger.warning("デプロイURLが閲覧できません: %s", deploy_url)

            logger.info("スプレッドシートを更新中...")
            self.spreadsheet.update_deploy_url(case["row_number"], deploy_url)

            self.spreadsheet.update_ai_status(case["row_number"], "完了")

            logger.info("案件処理が完了しました: %s", deploy_url)
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
                    f"エラー: {str(e)[:50]}",
                )
            except Exception as sheet_err:
                logger.warning(
                    "エラー後のスプレッドシートステータス更新に失敗 row=%s: %s",
                    case.get("row_number"),
                    sheet_err,
                    exc_info=True,
                )
            return None

    def run(self) -> None:
        """メイン処理を実行"""
        try:
            logger.info("Botを起動しました")

            cases = self.spreadsheet.get_pending_cases()

            if not cases:
                logger.info("処理対象の案件がありません")
                return

            if BOT_MAX_CASES:
                cases = cases[:BOT_MAX_CASES]
                logger.info(
                    "BOT_MAX_CASES=%s のため、先頭 %s 件のみ処理します",
                    BOT_MAX_CASES,
                    len(cases),
                )

            logger.info("%s件の案件を処理します", len(cases))

            for case in cases:
                try:
                    self.process_case(case)
                except Exception as e:
                    logger.error(
                        "案件ループ例外 row=%s record=%s: %s",
                        case.get("row_number"),
                        case.get("record_number"),
                        e,
                        exc_info=True,
                    )
                    continue

            logger.info("すべての案件処理が完了しました")

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
                print("ERROR: 列見出し不一致のため終了（SPREADSHEET_HEADERS_STRICT=true）")
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
                "config.py の SPREADSHEET_HEADER_LABELS をシート1行目に合わせるか、"
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
