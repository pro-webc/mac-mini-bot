"""スプレッドシート列マッピング・見出し定義。

列位置はシート1行目の見出しから自動検出される（``modules.spreadsheet_schema.resolve_columns_from_header_row``）。
``config.config`` から re-export されるため、既存の import は変更不要。
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# 全フィールド → 1行目に期待する見出しテキスト（auto-detect のソース）
# ---------------------------------------------------------------------------
SPREADSHEET_HEADER_LABELS: dict[str, str] = {
    "record_number": "record_id",
    "partner_name": "client_name",
    "contract_plan": "plan_type",
    "ball_holder": "ball_holder",
    "ai_status": "active_polish",
    "phase_status": "overall_status",
    "phase_deadline": "phase_deadline",
    "appo_memo": "ap_recording_memo",
    "sales_notes": "sales_note_pre_demo",
    "hearing_sheet_url": "hearing_sheet_url",
    "github_repo_url": "git_repo_url",
    "test_site_url": "test_url",
    "correction_tool_url": "revision_tool_url",
}

# deploy_url は test_site_url と同じ列（読み取り・書き込み兼用）
SPREADSHEET_COLUMN_ALIASES: dict[str, str] = {
    "deploy_url": "test_site_url",
}

# 全フィールド名（ヘッダー＋エイリアス）
ALL_SPREADSHEET_FIELDS: frozenset[str] = (
    frozenset(SPREADSHEET_HEADER_LABELS) | frozenset(SPREADSHEET_COLUMN_ALIASES)
)

# Bot が書き込んでよいフィールド名
BOT_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "ai_status", "deploy_url", "github_repo_url", "correction_tool_url",
})

# ---------------------------------------------------------------------------
# 必須案件フィールド（env で上書き可）
# ---------------------------------------------------------------------------
_raw_req_fields = os.getenv(
    "SPREADSHEET_REQUIRED_FIELDS",
    "record_number,partner_name,contract_plan",
)
SPREADSHEET_REQUIRED_CASE_FIELDS: tuple[str, ...] = tuple(
    k.strip()
    for k in _raw_req_fields.split(",")
    if k.strip() and k.strip() in ALL_SPREADSHEET_FIELDS
)
if not SPREADSHEET_REQUIRED_CASE_FIELDS:
    SPREADSHEET_REQUIRED_CASE_FIELDS = (
        "record_number",
        "partner_name",
        "contract_plan",
    )
