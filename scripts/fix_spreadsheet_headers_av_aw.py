#!/usr/bin/env python3
"""
1 行目の AV・AW に、config の SPREADSHEET_HEADER_LABELS（mac-mini / デプロイURL）を書き込む。

  python scripts/fix_spreadsheet_headers_av_aw.py

※ Google Sheets の編集権限がある認証（.env の GOOGLE_SHEETS_*）が必要です。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    from config.config import SPREADSHEET_COLUMNS, SPREADSHEET_HEADER_LABELS
    from modules.spreadsheet import SpreadsheetClient
    from modules.spreadsheet_schema import a1_range

    av = SPREADSHEET_COLUMNS["ai_status"]
    aw = SPREADSHEET_COLUMNS["deploy_url"]
    label_av = SPREADSHEET_HEADER_LABELS["ai_status"]
    label_aw = SPREADSHEET_HEADER_LABELS["deploy_url"]

    client = SpreadsheetClient()
    rng = a1_range(client.sheet_name, f"{av}1:{aw}1")
    body = {"values": [[label_av, label_aw]]}

    client.service.spreadsheets().values().update(
        spreadsheetId=client.spreadsheet_id,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

    print(f"OK: {rng} ← {label_av!r}, {label_aw!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
