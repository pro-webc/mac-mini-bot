"""フェーズ1スナップショット（extract_hearing_bundle）の単体テスト"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from config.config import latest_preflight_cases_path
from modules import phase1_hearing_snapshot as m


class _FakeSpecGen:
    def fetch_hearing_sheet(self, url: str) -> str | None:
        if "example.com" in url:
            return "fetched-body"
        return None


def test_latest_preflight_cases_path_missing(tmp_path: Path) -> None:
    assert latest_preflight_cases_path(run_root=tmp_path) is None


def test_latest_preflight_cases_path_finds_file(tmp_path: Path) -> None:
    snap = tmp_path / "preflight_snapshots" / "2020T1"
    snap.mkdir(parents=True)
    f = snap / "04_pending_cases.json"
    f.write_text("[]", encoding="utf-8")
    assert latest_preflight_cases_path(run_root=tmp_path) == f.resolve()


def test_snapshot_phase1_writes_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("modules.phase1_hearing_snapshot.SpecGenerator", lambda: _FakeSpecGen())

    cases = tmp_path / "04.json"
    cases.write_text(
        json.dumps(
            [
                {
                    "row_number": 10,
                    "record_number": "R1",
                    "partner_name": "P",
                    "contract_plan": "BASIC",
                    "hearing_sheet_url": "https://example.com/h",
                    "appo_memo": "memo",
                    "sales_notes": "sales",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    out = m.snapshot_phase1_from_cases_json(
        cases,
        case_index=0,
        output_root=tmp_path / "phase1_out",
    )

    assert (out / "hearing_sheet_content.txt").read_text(encoding="utf-8") == "fetched-body"
    assert (out / "appo_memo.txt").read_text(encoding="utf-8") == "memo"
    assert (out / "sales_notes.txt").read_text(encoding="utf-8") == "sales"
    data = json.loads((out / "02_hearing_bundle_summary.json").read_text(encoding="utf-8"))
    assert data["hearing_non_empty"] is True
    assert data["would_skip_in_main"] is False
    assert data["hearing_sheet_content_chars"] == len("fetched-body")


def test_snapshot_phase1_empty_hearing_flags_skip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("modules.phase1_hearing_snapshot.SpecGenerator", lambda: _FakeSpecGen())

    cases = tmp_path / "04.json"
    cases.write_text(
        json.dumps(
            [
                {
                    "row_number": 1,
                    "record_number": "R",
                    "partner_name": "P",
                    "contract_plan": "BASIC",
                    "hearing_sheet_url": "",
                    "appo_memo": "",
                    "sales_notes": "",
                }
            ]
        ),
        encoding="utf-8",
    )

    out = m.snapshot_phase1_from_cases_json(
        cases,
        output_root=tmp_path / "phase1_out",
    )
    data = json.loads((out / "02_hearing_bundle_summary.json").read_text(encoding="utf-8"))
    assert data["would_skip_in_main"] is True
    assert (out / "hearing_sheet_content.txt").read_text(encoding="utf-8") == ""
