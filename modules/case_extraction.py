"""ヒアリングシート類の抽出（スプレッドシート行 → LLM 投入用テキスト）。

TEXT_LLM 工程の前段。URL 取得や将来の OCR / 構造化抽出はここに集約する。
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from config.types import CaseRecord


@dataclass(frozen=True)
class ExtractedHearingBundle:
    """LLM に渡すヒアリング関連テキスト块。"""

    hearing_sheet_content: str
    appo_memo: str
    sales_notes: str


_BLOG_QUESTION_RE = re.compile(
    r"【\d+】[^\n]*ブログ[^\n]*\n+\s*(?:→|⇒|>|A[:：]?)?\s*(.+)",
    re.IGNORECASE,
)

_BLOG_POSITIVE_RE = re.compile(
    r"ブログ.{0,20}(?:はい|希望|利用|つけ|ほしい|欲しい|必要|設置|実装|あり|yes)",
    re.IGNORECASE,
)
_BLOG_NEGATIVE_RE = re.compile(
    r"ブログ.{0,20}(?:いいえ|不要|いらな|なし|無し|しない|不必要|no(?!te))",
    re.IGNORECASE,
)

_POSITIVE_ANSWERS = {"はい", "yes", "利用する", "希望する", "する", "あり", "o", "○"}
_NEGATIVE_ANSWERS = {"いいえ", "no", "利用しない", "不要", "しない", "なし", "x", "×", "無"}


def detect_blog_desired(
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> bool:
    """ヒアリングシート・アポメモ・営業メモなど全情報源から、ブログ実装希望の有無を判定する。

    先方が明確にブログを希望している場合のみ True を返す。
    ブログに関する言及がない・曖昧・否定的な場合は False（ブログなし）。
    """
    sources = [
        (hearing_sheet_content or "").strip(),
        (appo_memo or "").strip(),
        (sales_notes or "").strip(),
    ]
    combined = "\n".join(s for s in sources if s)
    if not combined:
        return False

    if "ブログ" not in combined:
        return False

    m = _BLOG_QUESTION_RE.search(combined)
    if m:
        answer = m.group(1).strip().rstrip("。、.").strip().lower()
        if answer in _POSITIVE_ANSWERS:
            return True
        return False

    if _BLOG_NEGATIVE_RE.search(combined):
        return False

    if _BLOG_POSITIVE_RE.search(combined):
        return True

    return False


def extract_hearing_bundle(
    case: CaseRecord,
    *,
    fetch_hearing_sheet: Callable[[str], str | None],
) -> ExtractedHearingBundle:
    """
    案件1行からヒアリングシート本文・アポメモ・営業メモを取り出す。

    Args:
        case: スプレッドシートの1行
        fetch_hearing_sheet: URL または貼り付け本文を解釈してテキストを返す関数
    """
    content = ""
    url = case.get("hearing_sheet_url")
    if url:
        content = fetch_hearing_sheet(str(url).strip()) or ""
    return ExtractedHearingBundle(
        hearing_sheet_content=content,
        appo_memo=str(case.get("appo_memo") or ""),
        sales_notes=str(case.get("sales_notes") or ""),
    )
