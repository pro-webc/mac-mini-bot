"""スプレッドシート列マッピング・見出し定義。

``config.config`` から re-export されるため、既存の import は変更不要。
"""
from __future__ import annotations

import os

SPREADSHEET_COLUMNS = {
    "record_number": "B",
    "partner_name": "C",
    "contract_plan": "D",
    "ball_holder": "Q",
    "ai_status": "R",
    "phase_status": "M",
    "phase_deadline": "T",
    "appo_memo": "AD",
    "sales_notes": "AE",
    "hearing_sheet_url": "AH",
    "github_repo_url": "AI",
    "test_site_url": "AJ",
    "deploy_url": "AJ",
}

SPREADSHEET_HEADER_LABELS: dict[str, str] = {
    "record_number": "record_id",
    "partner_name": "client_name",
    "contract_plan": "plan_type",
    "ball_holder": "ball_holder",
    "phase_status": "overall_status",
    "phase_deadline": "phase_deadline",
    "appo_memo": "ap_recording_memo",
    "sales_notes": "sales_note_pre_demo",
    "hearing_sheet_url": "hearing_sheet_url",
    "test_site_url": "test_url",
}

_raw_req_fields = os.getenv(
    "SPREADSHEET_REQUIRED_FIELDS",
    "record_number,partner_name,contract_plan",
)
SPREADSHEET_REQUIRED_CASE_FIELDS: tuple[str, ...] = tuple(
    k.strip()
    for k in _raw_req_fields.split(",")
    if k.strip() and k.strip() in SPREADSHEET_COLUMNS
)
if not SPREADSHEET_REQUIRED_CASE_FIELDS:
    SPREADSHEET_REQUIRED_CASE_FIELDS = (
        "record_number",
        "partner_name",
        "contract_plan",
    )
