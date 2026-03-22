"""phase2_text_llm_snapshot: フェーズ1成果物からの読み込み・作業分岐解決。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from config.config import pipeline_run_root_from_phase1_snapshot_dir
from modules.contract_workflow import ContractWorkBranch
from modules.phase2_text_llm_snapshot import (
    contract_work_branch_from_final_field,
    find_work_branch_row_for_record,
    infer_latest_work_branches_json,
    load_hearing_bundle_from_phase1_dir,
    load_phase1_case_meta,
    resolve_work_branch_for_phase2_replay,
)


def test_load_hearing_bundle_from_phase1_dir(tmp_path: Path) -> None:
    d = tmp_path / "p1"
    d.mkdir()
    (d / "hearing_sheet_content.txt").write_text("H", encoding="utf-8")
    (d / "appo_memo.txt").write_text("A", encoding="utf-8")
    (d / "sales_notes.txt").write_text("S", encoding="utf-8")
    b = load_hearing_bundle_from_phase1_dir(d)
    assert b.hearing_sheet_content == "H"
    assert b.appo_memo == "A"
    assert b.sales_notes == "S"


def test_load_phase1_case_meta(tmp_path: Path) -> None:
    d = tmp_path / "p1"
    d.mkdir()
    meta = {"record_number": "1", "contract_plan": "BASIC(9,800円)"}
    (d / "01_case_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8"
    )
    assert load_phase1_case_meta(d) == meta


def test_contract_work_branch_from_final_field() -> None:
    assert contract_work_branch_from_final_field("standard") == ContractWorkBranch.STANDARD
    assert contract_work_branch_from_final_field("BASIC_LP") == ContractWorkBranch.BASIC_LP
    with pytest.raises(ValueError):
        contract_work_branch_from_final_field("nope")


def test_find_work_branch_row_for_record(tmp_path: Path) -> None:
    p = tmp_path / "wb.json"
    p.write_text(
        json.dumps(
            [
                {"record_number": "9", "branch_final": "basic"},
                {"record_number": "10", "branch_final": "advance"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    row = find_work_branch_row_for_record(p, "10")
    assert row is not None
    assert row["branch_final"] == "advance"
    assert find_work_branch_row_for_record(p, "missing") is None


def test_infer_latest_work_branches_json(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    wb = run_root / "work_branch_snapshots" / "t1"
    wb.mkdir(parents=True)
    (wb / "01_work_branches.json").write_text("[]", encoding="utf-8")
    phase1 = run_root / "phase1_snapshots" / "t2"
    phase1.mkdir(parents=True)
    got = infer_latest_work_branches_json(phase1)
    assert got == wb / "01_work_branches.json"


def test_resolve_work_branch_for_phase2_replay_uses_json(tmp_path: Path) -> None:
    wb = tmp_path / "wb.json"
    wb.write_text(
        json.dumps(
            [{"record_number": "42", "branch_final": "basic_lp"}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    meta = {
        "record_number": "42",
        "contract_plan": "BASIC(9,800円)",
        "partner_name": "X",
    }
    branch, src = resolve_work_branch_for_phase2_replay(
        meta,
        work_branches_json=wb,
        use_spreadsheet_when_no_wb_row=False,
    )
    assert branch == ContractWorkBranch.BASIC_LP
    assert src == "work_branch_json"


def test_resolve_work_branch_for_phase2_replay_contract_plan_only() -> None:
    meta = {
        "record_number": "1",
        "contract_plan": "STANDARD(14,800円)",
        "partner_name": "Y",
    }
    branch, src = resolve_work_branch_for_phase2_replay(
        meta,
        work_branches_json=None,
        use_spreadsheet_when_no_wb_row=False,
    )
    assert branch == ContractWorkBranch.STANDARD
    assert src == "contract_plan_only"


def test_pipeline_run_root_from_phase1_snapshot_dir(tmp_path: Path) -> None:
    run = tmp_path / "run"
    p1 = run / "phase1_snapshots" / "t1"
    p1.mkdir(parents=True)
    assert pipeline_run_root_from_phase1_snapshot_dir(p1) == run.resolve()
    assert pipeline_run_root_from_phase1_snapshot_dir(tmp_path / "orphan") is None
