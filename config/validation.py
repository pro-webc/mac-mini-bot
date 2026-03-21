"""起動時設定の検証（フェイルファスト・警告の分離）"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

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

    # --- ローカルビルド ---
    if cfg.SITE_BUILD_ENABLED and not shutil.which("npm"):
        r.warnings.append(
            "SITE_BUILD_ENABLED=true ですが npm が PATH にありません。ビルド検証は失敗します。"
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
