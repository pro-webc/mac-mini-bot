#!/usr/bin/env python3
"""
全フィールドの見出しラベルを SPREADSHEET_HEADER_LABELS に合わせて1行目に書き込む。

列位置は自動検出の前提が整っていない場合でも動くよう、既定位置に書き込む。
既に見出しが入っているセルも上書きされるため注意。

  python scripts/fix_spreadsheet_headers_av_aw.py

※ Google Sheets の編集権限がある認証（.env の GOOGLE_SHEETS_*）が必要です。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


# 既定の列位置（自動検出前のブートストラップ用）
_DEFAULT_COLUMN_POSITIONS: dict[str, str] = {
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
    "correction_tool_url": "AK",
}


def main() -> int:
    from config.config import SPREADSHEET_HEADER_LABELS
    from modules.spreadsheet_schema import a1_range, column_letter_to_index

    from modules.spreadsheet import SpreadsheetClient

    client = object.__new__(SpreadsheetClient)
    client.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    client.sheet_name = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "Sheet1").strip() or "Sheet1"

    from google.auth import default as google_auth_default
    from googleapiclient.discovery import build

    auth_mode = os.getenv("GOOGLE_SHEETS_AUTH_MODE", "service_account").strip().lower()
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if auth_mode == "application_default":
        quota = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip() or None
        credentials, _ = google_auth_default(scopes=scopes, quota_project_id=quota)
    else:
        from google.oauth2 import service_account

        creds_path = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_PATH",
            "credentials/google-credentials.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=scopes
        )
    client.service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    data_entries = []
    for field, letter in sorted(_DEFAULT_COLUMN_POSITIONS.items(), key=lambda x: column_letter_to_index(x[1])):
        label = SPREADSHEET_HEADER_LABELS.get(field, field)
        rng = a1_range(client.sheet_name, f"{letter}1")
        data_entries.append({"range": rng, "values": [[label]]})

    client.service.spreadsheets().values().batchUpdate(
        spreadsheetId=client.spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": data_entries,
        },
    ).execute()

    written = {e["range"]: e["values"][0][0] for e in data_entries}
    print(f"OK: 見出しを書き込みました: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
