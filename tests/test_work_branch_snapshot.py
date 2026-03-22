"""work_branch スナップショット（契約プラン作業分岐の一括出力）"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from modules import work_branch_snapshot as m


def test_cases_json_path_from_phase1_snapshot_dir(tmp_path: Path) -> None:
    cases = tmp_path / "04.json"
    cases.write_text("[]", encoding="utf-8")
    phase1 = tmp_path / "phase1_run"
    phase1.mkdir()
    (phase1 / "00_source.json").write_text(
        json.dumps({"cases_json": str(cases), "case_index": 0, "cases_total": 0}),
        encoding="utf-8",
    )
    assert m.cases_json_path_from_phase1_snapshot_dir(phase1) == cases.resolve()


class _FakeSpreadsheet:
    def lookup_basic_is_landing_page(self, _r: str, _p: str) -> bool | None:
        return None


class _FakeSpreadsheetLp:
    def lookup_basic_is_landing_page(self, _r: str, _p: str) -> bool | None:
        return True


def test_snapshot_work_branches_writes_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "modules.work_branch_snapshot.SpreadsheetClient",
        lambda: _FakeSpreadsheet(),
    )
    cases = tmp_path / "04.json"
    cases.write_text(
        json.dumps(
            [
                {
                    "row_number": 1,
                    "record_number": "R1",
                    "partner_name": "P",
                    "contract_plan": "STANDARD(14,800円)",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    out = m.snapshot_work_branches_from_cases_json(
        cases,
        output_root=tmp_path / "wb_out",
        phase1_snapshot_dir=tmp_path / "dummy_phase1",
    )
    meta = json.loads((out / "00_source.json").read_text(encoding="utf-8"))
    assert Path(meta["phase1_snapshot_dir"]).name == "dummy_phase1"
    data = json.loads((out / "01_work_branches.json").read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["branch_final"] == "standard"
    assert data[0]["plan_info_name"] == "STANDARD"


def test_snapshot_basic_overridden_to_lp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "modules.work_branch_snapshot.SpreadsheetClient",
        lambda: _FakeSpreadsheetLp(),
    )
    cases = tmp_path / "04.json"
    cases.write_text(
        json.dumps(
            [
                {
                    "row_number": 2,
                    "record_number": "R2",
                    "partner_name": "Q",
                    "contract_plan": "BASIC",
                }
            ]
        ),
        encoding="utf-8",
    )
    out = m.snapshot_work_branches_from_cases_json(
        cases,
        output_root=tmp_path / "wb_out2",
    )
    data = json.loads((out / "01_work_branches.json").read_text(encoding="utf-8"))
    assert data[0]["branch_final"] == "basic_lp"
    assert data[0]["basic_overridden_to_lp"] is True
