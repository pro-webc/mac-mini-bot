"""フェーズ期限日のパースと着手下限日（config）の前提。"""
from __future__ import annotations

from datetime import date

import pytest

from modules.spreadsheet import parse_spreadsheet_phase_deadline_cell


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", None),
        ("  ", None),
        ("2026-03-27", date(2026, 3, 27)),
        ("2026/3/27", date(2026, 3, 27)),
        ("2026/03/27", date(2026, 3, 27)),
        ("3/27/2026", date(2026, 3, 27)),
        ("2026.03.27", date(2026, 3, 27)),
        ("46108", date(2026, 3, 27)),
        ("not a date", None),
    ],
)
def test_parse_spreadsheet_phase_deadline_cell(raw: str, expected: date | None) -> None:
    assert parse_spreadsheet_phase_deadline_cell(raw) == expected


def test_config_default_min_phase_deadline_is_disabled() -> None:
    """未設定時はフィルタ無効（None）。ハードコード日付で正しい案件を除外しないことを保証。"""
    from config import config as cfg

    assert cfg.SPREADSHEET_MIN_PHASE_DEADLINE is None
