"""スプレッドシート行など、境界で受け渡すデータの型（TypedDict）"""
from __future__ import annotations

from typing import TypedDict


class CaseRecord(TypedDict, total=False):
    """処理対象案件の1行分（キー欠落は実行時エラーになる想定で total=False）"""

    row_number: int
    record_number: str
    partner_name: str
    contract_plan: str
    ball_holder: str
    hearing_sheet_url: str
    appo_memo: str
    sales_notes: str
