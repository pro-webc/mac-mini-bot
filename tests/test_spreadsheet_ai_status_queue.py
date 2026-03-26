"""R 列（Bot 着手フラグ）のキュー除外判定"""

from __future__ import annotations

from unittest.mock import MagicMock

from modules.spreadsheet import SpreadsheetClient, ai_cell_excludes_from_pending_queue


def test_queue_excludes_any_non_empty_value() -> None:
    assert ai_cell_excludes_from_pending_queue("MacBot")
    assert ai_cell_excludes_from_pending_queue("完了")
    assert ai_cell_excludes_from_pending_queue("処理中")
    assert ai_cell_excludes_from_pending_queue("エラー: 失敗")
    assert ai_cell_excludes_from_pending_queue("スキップ: 理由")
    assert ai_cell_excludes_from_pending_queue("デモサイト制作中")


def test_queue_includes_empty_and_whitespace_only() -> None:
    assert not ai_cell_excludes_from_pending_queue("")
    assert not ai_cell_excludes_from_pending_queue("   ")
    assert not ai_cell_excludes_from_pending_queue(None)


def test_get_ai_status_cell_returns_trimmed_value(monkeypatch) -> None:
    """Sheets API の get 応答から ai_status セル1件を読む。"""
    monkeypatch.setattr(
        "modules.spreadsheet.GOOGLE_SHEETS_AUTH_MODE", "service_account", raising=False
    )
    monkeypatch.setattr(
        "modules.spreadsheet.GOOGLE_SHEETS_CREDENTIALS_PATH",
        "/nonexistent.json",
        raising=False,
    )

    fake_values = MagicMock()
    fake_values.execute = MagicMock(
        return_value={"values": [["  MacBot  "]]}
    )
    fake_get = MagicMock(return_value=fake_values)
    fake_spreadsheets = MagicMock()
    fake_spreadsheets.values = MagicMock(return_value=MagicMock(get=fake_get))
    fake_service = MagicMock()
    fake_service.spreadsheets = MagicMock(return_value=fake_spreadsheets)

    client = object.__new__(SpreadsheetClient)
    client.service = fake_service
    client.spreadsheet_id = "sid"
    client.sheet_name = "メイン"
    from config.spreadsheet_schema import BOT_WRITABLE_FIELDS
    from modules.spreadsheet_schema import (
        column_index_to_letters,
        max_column_index_for_map,
    )

    client.columns = {
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
        "correction_tool_url": "AK",
    }
    client._max_col_index = max_column_index_for_map(client.columns.values())
    client._data_range_end = column_index_to_letters(client._max_col_index)
    client._bot_writable_letters = frozenset(
        client.columns[f] for f in BOT_WRITABLE_FIELDS if f in client.columns
    )

    assert client.get_ai_status_cell(100) == "MacBot"
