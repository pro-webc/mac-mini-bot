"""AV 列のキュー除外判定（表記ゆれ）"""

from __future__ import annotations

from unittest.mock import MagicMock

from modules.spreadsheet import SpreadsheetClient, ai_cell_excludes_from_pending_queue


def test_queue_excludes_exact_complete_and_processing() -> None:
    assert ai_cell_excludes_from_pending_queue("完了")
    assert ai_cell_excludes_from_pending_queue("処理中")


def test_queue_excludes_complete_with_trailing_punctuation() -> None:
    assert ai_cell_excludes_from_pending_queue("完了！")
    assert ai_cell_excludes_from_pending_queue("完了。")
    assert ai_cell_excludes_from_pending_queue("  完了。  ")


def test_queue_excludes_error_and_skip_prefix() -> None:
    assert ai_cell_excludes_from_pending_queue("エラー: 失敗")
    assert ai_cell_excludes_from_pending_queue("スキップ: 理由")


def test_queue_includes_empty_and_non_terminal() -> None:
    assert not ai_cell_excludes_from_pending_queue("")
    assert not ai_cell_excludes_from_pending_queue("   ")
    assert not ai_cell_excludes_from_pending_queue("デモサイト制作中")


def test_get_ai_status_cell_returns_trimmed_value(monkeypatch) -> None:
    """Sheets API の get 応答から AV セル1件を読む。"""
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
        return_value={"values": [["  処理中  "]]}
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
    from modules.spreadsheet import SPREADSHEET_COLUMNS
    from modules.spreadsheet_schema import (
        column_index_to_letters,
        max_column_index_for_map,
    )

    client._max_col_index = max_column_index_for_map(SPREADSHEET_COLUMNS.values())
    client._data_range_end = column_index_to_letters(client._max_col_index)

    assert client.get_ai_status_cell(100) == "処理中"
