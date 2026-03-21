"""ヒアリングシート類の抽出（スプレッドシート行 → LLM 投入用テキスト）。

TEXT_LLM 工程の前段。URL 取得や将来の OCR / 構造化抽出はここに集約する。
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from config.types import CaseRecord


@dataclass(frozen=True)
class ExtractedHearingBundle:
    """LLM に渡すヒアリング関連テキスト块。"""

    hearing_sheet_content: str
    appo_memo: str
    sales_notes: str


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
