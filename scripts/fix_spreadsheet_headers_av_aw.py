#!/usr/bin/env python3
"""
AV・AW の 1 行目に任意の見出しを書き込む（人間向けラベル用）。

Bot は AV/AW の見出しを検証しません。空のままでも起動・書き込みに問題ありません。

  python scripts/fix_spreadsheet_headers_av_aw.py

※ Google Sheets の編集権限がある認証（.env の GOOGLE_SHEETS_*）が必要です。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

# config では検証しないが、チームで見出しを付けたい場合の既定文言
_DEFAULT_AV_LABEL = "mac-mini"
_DEFAULT_AW_LABEL = "デプロイURL"


def main() -> int:
    from config.config import SPREADSHEET_COLUMNS
    from modules.spreadsheet import SpreadsheetClient
    from modules.spreadsheet_schema import a1_range

    av = SPREADSHEET_COLUMNS["ai_status"]
    aw = SPREADSHEET_COLUMNS["deploy_url"]

    client = SpreadsheetClient()
    rng = a1_range(client.sheet_name, f"{av}1:{aw}1")
    body = {"values": [[_DEFAULT_AV_LABEL, _DEFAULT_AW_LABEL]]}

    client.service.spreadsheets().values().update(
        spreadsheetId=client.spreadsheet_id,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

    print(f"OK: {rng} ← {_DEFAULT_AV_LABEL!r}, {_DEFAULT_AW_LABEL!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
