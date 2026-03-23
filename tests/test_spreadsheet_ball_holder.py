"""Q 列ボール保持者（キュー条件）"""
from __future__ import annotations

from unittest.mock import patch

from modules.spreadsheet import ball_holder_cell_matches_queue_requirement


def test_ball_holder_matches_polish_default() -> None:
    with patch("modules.spreadsheet.SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT", "ポリッシュ"):
        assert ball_holder_cell_matches_queue_requirement("ポリッシュ") is True
        assert ball_holder_cell_matches_queue_requirement(" ポリッシュ ") is True
        assert ball_holder_cell_matches_queue_requirement("ポリッシ") is False
        assert ball_holder_cell_matches_queue_requirement("") is False


def test_ball_holder_filter_off_when_required_empty() -> None:
    with patch("modules.spreadsheet.SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT", ""):
        assert ball_holder_cell_matches_queue_requirement("") is True
        assert ball_holder_cell_matches_queue_requirement("誰でも") is True
