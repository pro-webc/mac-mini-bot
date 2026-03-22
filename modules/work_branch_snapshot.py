"""プリフライトの ``04_pending_cases.json`` から契約プラン作業分岐（main と同じ）を保存する。"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import (
    get_contract_plan_info,
    latest_phase1_snapshot_dir,
    latest_preflight_cases_path,
    pipeline_work_branch_snapshots_base,
)
from config.logging_setup import configure_logging

configure_logging()

from modules.contract_workflow import (
    ContractWorkBranch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)
from modules.spreadsheet import SpreadsheetClient


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def cases_json_path_from_phase1_snapshot_dir(phase1_dir: Path) -> Path:
    """
    フェーズ1スナップショットの ``00_source.json`` に記録された ``cases_json``（04_pending_cases）の Path。
    """
    src = phase1_dir.resolve() / "00_source.json"
    if not src.is_file():
        raise FileNotFoundError(f"フェーズ1スナップショットに 00_source.json がありません: {src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    raw_path = (data.get("cases_json") or "").strip()
    if not raw_path:
        raise ValueError(f"00_source.json に cases_json がありません: {src}")
    return Path(raw_path).expanduser().resolve()


def snapshot_work_branches_from_cases_json(
    cases_json_path: Path,
    *,
    spreadsheet: SpreadsheetClient | None = None,
    output_root: Path | None = None,
    phase1_snapshot_dir: Path | None = None,
) -> Path:
    """
    ``04_pending_cases.json`` の各案件について、``main.process_case`` と同じ作業分岐を計算して JSON に保存する。

    BASIC のときは ``SpreadsheetClient.lookup_basic_is_landing_page`` を呼ぶ（Sheets API 使用）。
    """
    p = cases_json_path.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"cases JSON が見つかりません: {p}")

    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"JSON は非空のリストである必要があります: {p}")

    sheet = spreadsheet or SpreadsheetClient()
    base = output_root or pipeline_work_branch_snapshots_base()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    source_meta: dict[str, Any] = {"cases_json": str(p), "cases_total": len(raw)}
    if phase1_snapshot_dir is not None:
        source_meta["phase1_snapshot_dir"] = str(phase1_snapshot_dir.resolve())
    _write_json(out / "00_source.json", source_meta)

    rows: list[dict[str, Any]] = []
    for case in raw:
        if not isinstance(case, dict):
            continue
        plan_raw = (case.get("contract_plan") or "").strip()
        plan_info = get_contract_plan_info(plan_raw)
        before = resolve_contract_work_branch(case.get("contract_plan") or "")
        final = resolve_work_branch_with_basic_lp_override(
            case.get("contract_plan") or "",
            record_number=str(case.get("record_number") or ""),
            partner_name=str(case.get("partner_name") or ""),
            lookup_basic_is_landing_page=sheet.lookup_basic_is_landing_page,
        )
        rows.append(
            {
                "row_number": case.get("row_number"),
                "record_number": case.get("record_number"),
                "partner_name": case.get("partner_name"),
                "contract_plan_raw": plan_raw,
                "plan_info_name": plan_info.get("name"),
                "plan_info_pages": plan_info.get("pages"),
                "plan_info_type": plan_info.get("type"),
                "branch_after_resolve_contract_plan": before.value,
                "branch_final": final.value,
                "basic_overridden_to_lp": (
                    before == ContractWorkBranch.BASIC and final == ContractWorkBranch.BASIC_LP
                ),
            }
        )

    _write_json(out / "01_work_branches.json", rows)

    (out / "README.txt").write_text(
        "\n".join(
            [
                "契約プラン作業分岐スナップショット（main.process_case と同じ）",
                "",
                "00_source.json — 入力 cases_json・件数（フェーズ1経由なら phase1_snapshot_dir）",
                "01_work_branches.json — 各行の plan_info と branch_final",
                "",
                "BASIC かつサイトタイプシートで LP のときだけ branch_final が basic_lp に上書きされます。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def main_argv(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="04_pending_cases.json から作業分岐を算出し work_branch_snapshots に保存"
    )
    parser.add_argument(
        "cases_json",
        nargs="?",
        default=None,
        help="04_pending_cases.json（--from-phase1 無しで省略時は最新 preflight）",
    )
    parser.add_argument(
        "--from-phase1",
        nargs="?",
        const="",
        default=None,
        metavar="DIR",
        help=(
            "フェーズ1スナップショット1ランのディレクトリ。"
            "その 00_source.json の cases_json を入力にする。DIR 省略で最新 phase1_snapshots"
        ),
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "1 ラン用の親ディレクトリ（preflight / phase1 / work_branch の各 *_snapshots をその下に置く）。"
            " 省略時は PIPELINE_TEST_RUN_DIR または output/"
        ),
    )
    args = parser.parse_args(argv)

    rr = args.run_dir.resolve() if args.run_dir else None

    phase1_dir: Path | None = None
    path: Path | None

    if args.from_phase1 is not None:
        if args.from_phase1 == "":
            phase1_dir = latest_phase1_snapshot_dir(run_root=rr)
            if phase1_dir is None:
                print(
                    "ERROR: --from-phase1 のみ指定しましたが phase1_snapshots がありません",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"入力（最新フェーズ1）: {phase1_dir}")
        else:
            phase1_dir = Path(args.from_phase1)
            print(f"入力（フェーズ1指定）: {phase1_dir.resolve()}")
        path = cases_json_path_from_phase1_snapshot_dir(phase1_dir)
        print(f"04（フェーズ1経由）: {path}")
    elif args.cases_json:
        path = Path(args.cases_json)
    else:
        path = latest_preflight_cases_path(run_root=rr)
        if path is None:
            print(
                "ERROR: cases_json 未指定かつ preflight の 04 がありません",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"入力（最新 preflight）: {path}")

    out = snapshot_work_branches_from_cases_json(
        path,
        phase1_snapshot_dir=phase1_dir,
        output_root=pipeline_work_branch_snapshots_base(rr),
    )
    print(f"保存先: {out}")


if __name__ == "__main__":
    main_argv()
