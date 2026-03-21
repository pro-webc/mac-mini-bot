"""メインオーケストレーション"""
from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# logging_setup → config を読むため、config より前に CLI 用の環境変数を反映する
if "--skip-images" in sys.argv:
    os.environ["IMAGE_GEN_SKIP_RUN"] = "1"
    sys.argv = [a for a in sys.argv if a != "--skip-images"]

from config.logging_setup import configure_logging

configure_logging()

from config.log_theme import (
    all_done_banner,
    batch_start_banner,
    case_start_banner,
    idle_banner,
    startup_title,
    stream_supports_color,
)
from config.config import (
    BOT_DEPLOY_URL_SOURCE,
    BOT_MAX_CASES,
    IMAGE_GEN_SKIP_RUN,
    SITE_BUILD_ENABLED,
    SITE_IMPLEMENTATION_ENABLED,
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN,
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

_PREFLIGHT_OK = "__PREFLIGHT_OK__"


def _format_ai_status_error(exc: BaseException) -> str:
    """AV 列向けに例外メッセージを短く整形（モジュールパス連呼を削る）。"""
    msg = (str(exc) or type(exc).__name__).strip()
    for noise in (
        "（modules.requirement_extractor.extract_requirements）。",
        "（modules.requirement_extractor）。",
        "（modules.spec_generator.generate_spec）。",
        "（modules.spec_generator）。",
        " modules.requirement_extractor",
        " modules.spec_generator",
    ):
        msg = msg.replace(noise, "")
    msg = " ".join(msg.split())
    prefix = "エラー: "
    budget = max(24, SPREADSHEET_AI_STATUS_ERROR_MAX_LEN - len(prefix))
    if len(msg) > budget:
        msg = msg[: budget - 1] + "…"
    return prefix + msg


def _json_default(o: Any) -> Any:
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


class WebsiteBot:
    """Webサイト製作自動化Bot"""

    def __init__(self) -> None:
        """本番と同じく SpreadsheetClient を常に初期化する（プレフライトも同一 WebsiteBot を使う）。"""
        self.spreadsheet = SpreadsheetClient()
        self.requirement_extractor = RequirementExtractor()
        self.spec_generator = SpecGenerator()
        self.image_generator = ImageGenerator()
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
        """GitHub push 直前まで初期化しない（プレフライトで GITHUB_TOKEN 不要にするため）"""
        if self._github_client is None:
            self._github_client = GitHubClient()
        return self._github_client

    def _write_preflight_bundle(
        self,
        artifact_dir: Path,
        *,
        case: CaseRecord,
        hearing_sheet_content: str,
        requirements_result: dict[str, Any] | None,
        spec: dict[str, Any] | None,
        site_dir: Path | None,
        implementation: dict[str, Any] | None,
        build_verification: dict[str, Any] | None,
        images_payload: dict[str, Any] | None,
        error: dict[str, str] | None,
    ) -> None:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "hearing_sheet_content.txt").write_text(
            hearing_sheet_content, encoding="utf-8"
        )
        impl_log = (implementation or {}).get("log") or ""
        if impl_log:
            (artifact_dir / "implementation_log.txt").write_text(
                str(impl_log), encoding="utf-8"
            )
        if build_verification and (build_verification.get("log") or ""):
            (artifact_dir / "build_log.txt").write_text(
                str(build_verification["log"]), encoding="utf-8"
            )
        site_name = f"{case['partner_name']}-{case['record_number']}"
        meta: dict[str, Any] = {
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
            "stopped_before": "github_client.push_to_github",
            "artifact_folder": str(artifact_dir.resolve()),
            "partner_name": case.get("partner_name"),
            "record_number": case.get("record_number"),
            "row_number": case.get("row_number"),
            "site_name": site_name,
            "config": {
                "SITE_IMPLEMENTATION_ENABLED": SITE_IMPLEMENTATION_ENABLED,
                "SITE_BUILD_ENABLED": SITE_BUILD_ENABLED,
            },
        }
        if site_dir and site_dir.is_dir():
            site_dest = artifact_dir / "site"
            try:
                if site_dest.exists():
                    shutil.rmtree(site_dest)
                shutil.copytree(
                    site_dir,
                    site_dest,
                    symlinks=False,
                    ignore_dangling_symlinks=True,
                )
                meta["site_snapshot_copied_to"] = str(site_dest.resolve())
            except OSError as e:
                meta["site_snapshot_copy_error"] = str(e)
                logger.warning("プレフライト: site コピー失敗: %s", e)

        payload: dict[str, Any] = {
            "meta": meta,
            "inputs": {
                "hearing_sheet_url": case.get("hearing_sheet_url"),
                "hearing_sheet_content": hearing_sheet_content,
                "appo_memo": case.get("appo_memo", ""),
                "sales_notes": case.get("sales_notes", ""),
                "contract_plan": case.get("contract_plan"),
            },
            "requirements_result": requirements_result,
            "spec": spec,
            "site_generation": (
                {"site_dir": str(site_dir.resolve()), "site_name": site_name}
                if site_dir
                else None
            ),
            "implementation": implementation,
            "build_verification": build_verification,
            "images": images_payload,
            "error": error,
        }
        (artifact_dir / "preflight_full.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
            encoding="utf-8",
        )

    def process_case(
        self,
        case: CaseRecord,
        *,
        preflight_artifact_dir: Path | str | None = None,
    ) -> str | None:
        """
        案件を処理

        Args:
            case: 案件情報
            preflight_artifact_dir: 指定時は GitHub/Vercel/シート更新を行わず、
                このディレクトリへ成果物を保存して終了（戻り値は _PREFLIGHT_OK 定数）。

        Returns:
            デプロイURL（本番成功時） / プレフライト成功時は __PREFLIGHT_OK__。
            必須項目不足で着手しない場合のみ None。処理中の失敗は AV 列更新後に例外を再送出し、
            `run()` のバッチはそこで中断される。
        """
        artifact_dir = (
            Path(preflight_artifact_dir).resolve() if preflight_artifact_dir else None
        )
        preflight = artifact_dir is not None

        hearing_sheet_content = ""
        requirements_result: dict[str, Any] | None = None
        spec: dict[str, Any] | None = None
        site_dir: Path | None = None
        impl_log = ""
        build_verification: dict[str, Any] | None = None
        images_payload: dict[str, Any] | None = None

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
                    preflight=preflight,
                    use_color=_tty_color,
                )
            )

            if not preflight:
                self.spreadsheet.update_ai_status(case["row_number"], "処理中")

            logger.info("› ヒアリングシートを取得…")
            if case.get("hearing_sheet_url"):
                hearing_sheet_content = (
                    self.spec_generator.fetch_hearing_sheet(case["hearing_sheet_url"])
                    or ""
                )

            logger.info("› サイト制作プロンプトを設計（TEXT_LLM 第1段）…")
            requirements_result = self.requirement_extractor.extract_requirements(
                hearing_sheet_content,
                case.get("appo_memo", ""),
                case.get("sales_notes", ""),
                case["contract_plan"],
            )

            logger.info("› サイト台本を生成（TEXT_LLM 第2段・テキストライター／末尾YAML）…")
            spec = self.spec_generator.generate_spec(
                hearing_sheet_content,
                requirements_result,
                case["contract_plan"],
                case["partner_name"],
            )

            logger.info("› Next.js の技術土台を生成…")
            site_name = f"{case['partner_name']}-{case['record_number']}"
            site_dir = self.site_generator.generate_site(spec, [], site_name)

            if SITE_IMPLEMENTATION_ENABLED:
                logger.info("› サイト実装を実行（LLM がコードを書き込み）…")
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
                logger.info("› 実装はスキップ — npm build で検証のみ…")
                ok_b, blog = verify_site_build(site_dir)
                blog = blog or ""
                build_verification = {"ok": ok_b, "log": blog}
                if not ok_b:
                    raise RuntimeError(
                        "npm build に失敗: " + (blog[-2000:] if blog else "")
                    )

            if self.image_generator.is_enabled() and not IMAGE_GEN_SKIP_RUN:
                logger.info("› 画像パイプライン（別コンテキストで生成）…")
                entries, manifest_path = self.image_generator.generate_after_site(
                    site_dir
                )
                if SITE_BUILD_ENABLED:
                    ok_img_b, img_blog = verify_site_build(
                        site_dir, skip_install=True
                    )
                    images_payload = {
                        "entries": entries,
                        "manifest_path": str(manifest_path),
                        "post_image_build_ok": ok_img_b,
                        "post_image_build_log": img_blog or "",
                    }
                    if not ok_img_b:
                        raise RuntimeError(
                            "画像追加後の npm build に失敗しました。ログ末尾: "
                            + ((img_blog or "")[-2000:])
                        )
                else:
                    images_payload = {
                        "entries": entries,
                        "manifest_path": str(manifest_path),
                        "post_image_build_ok": None,
                        "post_image_build_log": "",
                    }
            else:
                if self.image_generator.is_enabled() and IMAGE_GEN_SKIP_RUN:
                    logger.info(
                        "› 画像パイプラインをスキップ（IMAGE_GEN_SKIP_RUN=true。"
                        " .env の IMAGE_GEN_ENABLED は変更していません）…"
                    )
                if preflight:
                    if self.image_generator.is_enabled() and IMAGE_GEN_SKIP_RUN:
                        images_payload = {
                            "skipped": True,
                            "reason": "IMAGE_GEN_SKIP_RUN（当該実行のみ画像工程をスキップ）",
                        }
                    else:
                        images_payload = {
                            "skipped": True,
                            "reason": "IMAGE_GEN_ENABLED=false 等",
                        }

            implementation_dict: dict[str, Any] | None = None
            if SITE_IMPLEMENTATION_ENABLED:
                implementation_dict = {"ok": True, "log": impl_log}

            if preflight and artifact_dir is not None:
                self._write_preflight_bundle(
                    artifact_dir,
                    case=case,
                    hearing_sheet_content=hearing_sheet_content,
                    requirements_result=requirements_result,
                    spec=spec,
                    site_dir=site_dir,
                    implementation=implementation_dict,
                    build_verification=build_verification,
                    images_payload=images_payload,
                    error=None,
                )
                logger.info(
                    "✓ プレフライト完了（GitHub 手前まで）成果物 → %s", artifact_dir
                )
                return _PREFLIGHT_OK

            logger.info("› GitHub にプッシュ…")
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
            if preflight and artifact_dir is not None:
                err = {"type": type(e).__name__, "message": str(e)}
                impl_on_err: dict[str, Any] | None = None
                if SITE_IMPLEMENTATION_ENABLED and impl_log:
                    impl_on_err = {"ok": False, "log": impl_log}
                self._write_preflight_bundle(
                    artifact_dir,
                    case=case,
                    hearing_sheet_content=hearing_sheet_content,
                    requirements_result=requirements_result,
                    spec=spec,
                    site_dir=site_dir,
                    implementation=impl_on_err,
                    build_verification=build_verification,
                    images_payload=images_payload,
                    error=err,
                )
                logger.info(
                    "⚠ プレフライト: エラーでも途中経過を保存しました → %s",
                    artifact_dir,
                )
            else:
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
