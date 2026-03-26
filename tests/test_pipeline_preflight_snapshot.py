"""preflight スナップショット（process_case 直前まで）の単体テスト"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from config.validation import StartupValidationResult


@pytest.fixture
def fake_startup_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    def _v(*, require_full_pipeline: bool = True) -> StartupValidationResult:
        return StartupValidationResult(errors=[], warnings=["test-warning"])

    monkeypatch.setattr(
        "modules.pipeline_preflight_snapshot.validate_startup_config",
        _v,
    )


class _FakeSpreadsheet:
    columns: dict[str, str] = {
        "record_number": "B",
        "partner_name": "C",
        "contract_plan": "D",
    }

    def get_pending_cases(self) -> list[dict[str, object]]:
        return [
            {
                "row_number": 1,
                "record_number": "REC1",
                "partner_name": "Partner",
                "contract_plan": "BASIC",
            },
            {
                "row_number": 2,
                "record_number": "REC2",
                "partner_name": "Partner",
                "contract_plan": "BASIC",
            },
        ]


def _fake_website_bot() -> object:
    bot = type("B", (), {})()
    bot.spreadsheet = _FakeSpreadsheet()
    return bot


def test_json_safe_roundtrip() -> None:
    from modules import pipeline_preflight_snapshot as m

    assert m._json_safe({"n": 1, "x": object()})["x"].startswith("<object")


def test_snapshot_preflight_writes_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_startup_ok: None,
) -> None:
    from modules import pipeline_preflight_snapshot as m

    monkeypatch.setattr("modules.pipeline_preflight_snapshot.WebsiteBot", _fake_website_bot)
    monkeypatch.setattr("modules.pipeline_preflight_snapshot.BOT_MAX_CASES", 1)

    root = tmp_path / "snap_root"
    out = m.snapshot_preflight_before_process_case(output_root=root)

    assert out.is_dir()
    assert (out / "01_startup_validation.json").is_file()
    assert (out / "02_resolved_columns.json").is_file()
    assert (out / "03_pending_cases_summary.json").is_file()
    assert (out / "04_pending_cases.json").is_file()
    assert (out / "README.txt").is_file()

    startup = json.loads((out / "01_startup_validation.json").read_text(encoding="utf-8"))
    assert startup["ok"] is True
    cols = json.loads((out / "02_resolved_columns.json").read_text(encoding="utf-8"))
    assert "columns" in cols
    summary = json.loads((out / "03_pending_cases_summary.json").read_text(encoding="utf-8"))
    assert summary["fetched_count"] == 2
    assert summary["after_bot_max_cases"] == 1
    cases = json.loads((out / "04_pending_cases.json").read_text(encoding="utf-8"))
    assert len(cases) == 1
