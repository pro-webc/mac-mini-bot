"""サイト修正ツール（site-annotator）へのサイト登録クライアント

Vercel デプロイ完了後、生成サイトを site-annotator に登録する。
API は パートナー名一致・リポジトリURL検出・tracker.js 存在 の3チェックを
並列実行し、全通過時のみサイトを作成する。
"""
from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

_TIMEOUT_SEC = 30


class SiteProvisionError(Exception):
    """site-annotator API の既知エラー（400/401/403 等）"""

    def __init__(self, message: str, *, status_code: int, body: dict[str, Any]):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _log_check_failures(checks: dict[str, Any]) -> None:
    """400 レスポンスの checks オブジェクトから失敗項目を個別にログ出力する。"""
    partner = checks.get("partner", {})
    if not partner.get("matched", True):
        suggestions = partner.get("suggestions", [])
        logger.warning(
            "  パートナー名不一致（候補: %s）",
            ", ".join(suggestions) if suggestions else "なし",
        )

    tracker = checks.get("tracker", {})
    if not tracker.get("detected", True):
        logger.warning("  tracker.js がサイト HTML から検出できませんでした")

    repo = checks.get("repo", {})
    if not repo.get("repo_url"):
        logger.warning("  リポジトリ URL を Vercel から検出できませんでした")


def provision_site(
    *,
    api_url: str,
    api_key: str,
    site_name: str,
    site_url: str,
) -> dict[str, Any]:
    """POST /api/sites/provision で生成サイトを site-annotator に登録する。

    Returns:
        201 時のレスポンス JSON（site / checks / crawl）。
    Raises:
        SiteProvisionError: 400（チェック失敗）/ 401（認証）/ 403（IP制限）等。
        requests.RequestException: ネットワーク障害等。
    """
    resp = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"name": site_name, "url": site_url},
        timeout=_TIMEOUT_SEC,
    )

    if resp.status_code == 201:
        data = resp.json()
        site_info = data.get("site", {})
        logger.info(
            "✓ site-annotator 登録完了 — id=%s, share_token=%s, crawl=%d件",
            site_info.get("id", "?"),
            site_info.get("share_token", "?"),
            data.get("crawl", {}).get("added", 0),
        )
        return data

    try:
        body = resp.json()
    except Exception:
        body = {"error": resp.text[:500]}

    error_msg = body.get("error", f"HTTP {resp.status_code}")

    if resp.status_code == 400:
        logger.warning("site-annotator 事前チェック失敗: %s", error_msg)
        _log_check_failures(body.get("checks", {}))
    elif resp.status_code == 401:
        logger.warning("site-annotator 認証エラー: %s", error_msg)
    elif resp.status_code == 403:
        logger.warning("site-annotator IP制限: %s", error_msg)

    raise SiteProvisionError(error_msg, status_code=resp.status_code, body=body)
