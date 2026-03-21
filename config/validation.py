"""起動時設定の検証（フェイルファスト・警告の分離）"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from modules.text_llm import is_text_llm_configured

from config import config as cfg


@dataclass
class StartupValidationResult:
    """検証結果"""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def validate_startup_config(*, require_full_pipeline: bool = True) -> StartupValidationResult:
    """
    本番実行前に必須環境を検証する。

    Args:
        require_full_pipeline: True のとき GitHub / Vercel / スプレッドシート必須。
            単体テストやドライランでは False。
    """
    r = StartupValidationResult()

    # --- テキスト LLM（要望抽出・仕様書・サイト実装）---
    if not is_text_llm_configured():
        r.errors.append(
            "テキスト LLM: TEXT_LLM_PROVIDER=cursor_agent_cli（既定）または claude_code_cli と、"
            "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
            "（`agent login` または CURSOR_API_KEY が必要な場合があります）"
        )

    _tlp = (os.getenv("TEXT_LLM_PROVIDER") or "").strip().lower()
    if _tlp and _tlp not in ("claude_code_cli", "cursor_agent_cli"):
        r.errors.append(
            f"TEXT_LLM_PROVIDER={_tlp!r} は未対応です。"
            "cursor_agent_cli または claude_code_cli のみ指定できます。"
        )

    # --- ローカルビルド ---
    if cfg.SITE_BUILD_ENABLED and not shutil.which("npm"):
        r.warnings.append(
            "SITE_BUILD_ENABLED=true ですが npm が PATH にありません。ビルド検証は失敗します。"
        )

    # --- 画像パイプライン ---
    if cfg.IMAGE_GEN_ENABLED:
        if cfg.IMAGE_GEN_PROVIDER in ("openai", "gemini"):
            key = cfg.resolve_image_gen_api_key(cfg.IMAGE_GEN_PROVIDER)
            if not key:
                r.warnings.append(
                    f"IMAGE_GEN_ENABLED=true かつ IMAGE_GEN_PROVIDER={cfg.IMAGE_GEN_PROVIDER} ですが、"
                    "IMAGE_GEN_API_KEY が空で、IMAGE_GEN_ALLOW_FALLBACK_TO_MAIN_KEYS も false のため "
                    "API 画像生成はスキップされ PIL にフォールバックします。"
                )
        _igm_raw = os.getenv("IMAGE_GEN_MODE", "").strip().lower()
        if _igm_raw and _igm_raw not in ("from_placeholder_source", "standalone_spec"):
            r.warnings.append(
                f"IMAGE_GEN_MODE={_igm_raw!r} は無効です。from_placeholder_source として扱われます。"
            )

    # --- デプロイ系 ---
    if require_full_pipeline:
        if not cfg.GOOGLE_SHEETS_SPREADSHEET_ID.strip():
            r.errors.append("GOOGLE_SHEETS_SPREADSHEET_ID が空です。")

        if cfg.GOOGLE_SHEETS_AUTH_MODE == "service_account":
            creds = Path(cfg.GOOGLE_SHEETS_CREDENTIALS_PATH)
            if not creds.is_file():
                r.errors.append(
                    f"Google 認証ファイルが見つかりません: {creds}（GOOGLE_SHEETS_CREDENTIALS_PATH）"
                )
        elif cfg.GOOGLE_SHEETS_AUTH_MODE == "application_default":
            if not (cfg.GOOGLE_CLOUD_PROJECT or "").strip():
                r.errors.append(
                    "GOOGLE_SHEETS_AUTH_MODE=application_default のときは "
                    "GOOGLE_CLOUD_PROJECT（GCP プロジェクト ID）が必須です。"
                    "Sheets API を有効にしたプロジェクト ID を .env に設定してください。"
                    "（`gcloud config get-value project` で確認できます）"
                )

        if not cfg.GITHUB_TOKEN.strip():
            r.errors.append("GITHUB_TOKEN が空です。")

        if not cfg.GITHUB_USERNAME.strip():
            r.warnings.append("GITHUB_USERNAME が空です。GitHub 連携で問題になる場合があります。")

        if cfg.BOT_DEPLOY_URL_SOURCE == "vercel" and not cfg.VERCEL_TOKEN.strip():
            r.errors.append("VERCEL_TOKEN が空です（BOT_DEPLOY_URL_SOURCE=vercel 時は必須）。")
        if cfg.BOT_DEPLOY_URL_SOURCE == "github":
            r.warnings.append(
                "BOT_DEPLOY_URL_SOURCE=github — スプレッドシートには GitHub リポジトリ URL のみ記録され、"
                "Vercel デプロイは行いません。"
            )

    return r
