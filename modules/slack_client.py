"""Slack チャンネルとの連携クライアント

修正フローで使用。指定チャンネルのメッセージをレコード番号でフィルタし、
該当する修正指示テキストを返す。スレッドリプライも収集する。
修正完了後はスレッドに報告を投稿する。
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

# レコード番号の抽出パターン — 実データに基づく複数形式に対応
# - "レコード番号:16960" or "レコード番号：16960"（全角コロン）
# - "#12345 ..."
# - "12345\tパートナー名"（タブ区切り）
# - 先頭の数字列 "12345 ..."
_RECORD_NUMBER_RE = re.compile(
    r"(?:"
    r"レコード番号[:：]\s*(\d{4,6})"  # レコード番号:16960
    r"|(?:^|#)(\d{4,6})\b"            # #12345 or 先頭数字
    r")",
)


class SlackFetchError(Exception):
    """Slack API からのメッセージ取得エラー"""

    def __init__(self, message: str, *, error_code: str = ""):
        super().__init__(message)
        self.error_code = error_code


@dataclass
class CorrectionMessage:
    """1 件の修正指示メッセージ"""

    text: str
    ts: str
    user: str
    is_reply: bool


def extract_record_number(text: str) -> str | None:
    """メッセージテキストからレコード番号を抽出する。

    対応パターン:
      - "レコード番号:16960 パートナー名:..."
      - "レコード番号：16960"（全角コロン）
      - "#12345 電話番号を修正して"
      - "12345 ヘッダーの色を変更"
      - "16800\\tコンドミニアムとらや"（タブ区切り）
    見つからなければ None。
    """
    m = _RECORD_NUMBER_RE.search(text)
    if not m:
        return None
    return m.group(1) or m.group(2)


def fetch_correction_messages(
    *,
    token: str,
    channel_id: str,
    record_number: str,
    limit: int = 200,
) -> list[CorrectionMessage]:
    """指定チャンネルからレコード番号に一致する修正指示メッセージを取得する。

    Args:
        token: Slack Bot トークン (xoxb-...)
        channel_id: 修正指示チャンネルの ID
        record_number: 検索対象のレコード番号（文字列）
        limit: 取得するメッセージの最大件数

    Returns:
        該当する修正指示メッセージのリスト（時系列順）。
        スレッドの親メッセージが該当する場合、そのリプライも含む。

    Raises:
        SlackFetchError: Slack API エラー
    """
    client = WebClient(token=token)
    want = record_number.strip()

    try:
        resp = client.conversations_history(channel=channel_id, limit=limit)
    except SlackApiError as e:
        raise SlackFetchError(
            f"conversations.history 失敗: {e}",
            error_code=e.response.get("error", ""),
        ) from e

    messages: list[dict[str, Any]] = resp.get("messages", [])
    results: list[CorrectionMessage] = []

    for msg in messages:
        text = msg.get("text", "")
        found = extract_record_number(text)
        if found != want:
            continue

        results.append(CorrectionMessage(
            text=text,
            ts=msg["ts"],
            user=msg.get("user", ""),
            is_reply=False,
        ))

        # スレッドリプライを収集
        thread_ts = msg.get("thread_ts") or msg["ts"]
        reply_count = msg.get("reply_count", 0)
        if reply_count > 0:
            try:
                replies_resp = client.conversations_replies(
                    channel=channel_id, ts=thread_ts, limit=200,
                )
            except SlackApiError:
                logger.warning(
                    "スレッドリプライの取得に失敗しました ts=%s",
                    thread_ts, exc_info=True,
                )
                continue
            for reply in replies_resp.get("messages", [])[1:]:
                results.append(CorrectionMessage(
                    text=reply.get("text", ""),
                    ts=reply["ts"],
                    user=reply.get("user", ""),
                    is_reply=True,
                ))

    # 時系列順（ts 昇順）
    results.sort(key=lambda m: m.ts)

    logger.info(
        "Slack 修正指示取得: record=%s channel=%s hits=%d (うちリプライ %d)",
        want, channel_id, len(results),
        sum(1 for m in results if m.is_reply),
    )
    return results


def post_message(
    *,
    token: str,
    channel_id: str,
    text: str,
    thread_ts: str | None = None,
) -> dict[str, Any]:
    """Slack チャンネルにメッセージを投稿する。

    Args:
        token: Slack Bot トークン
        channel_id: 投稿先チャンネル ID
        text: 投稿テキスト
        thread_ts: スレッドの親メッセージ ts（指定時はスレッドリプライ）

    Returns:
        Slack API レスポンス

    Raises:
        SlackFetchError: API エラー
    """
    client = WebClient(token=token)
    try:
        kwargs: dict[str, Any] = {"channel": channel_id, "text": text}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        resp = client.chat_postMessage(**kwargs)
        logger.info(
            "Slack メッセージ投稿: channel=%s thread=%s",
            channel_id, thread_ts or "(新規)",
        )
        return resp.data
    except SlackApiError as e:
        raise SlackFetchError(
            f"chat.postMessage 失敗: {e}",
            error_code=e.response.get("error", ""),
        ) from e
