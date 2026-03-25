"""フェーズ1スナップショットを入力に TEXT_LLM（フェーズ2）だけ実行し結果を保存する。

工程テスト（``pipeline_test_snapshots``）で保存した ``phase1_snapshots/<UTC>/`` の
``.txt`` / ``01_case_meta.json`` を読み、任意で ``work_branch_snapshots/*/01_work_branches.json``
の ``branch_final`` で本番と同じ作業分岐を再現する。
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import (
    latest_phase1_snapshot_dir,
    pipeline_phase2_snapshots_base,
)

from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import (
    ContractWorkBranch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)
from modules.llm.llm_text_artifacts import write_llm_yaml_artifact
from modules.llm.text_llm_stage import run_text_llm_stage
from modules.spreadsheet import SpreadsheetClient

logger = logging.getLogger(__name__)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_hearing_bundle_from_phase1_dir(phase1_dir: Path) -> ExtractedHearingBundle:
    """フェーズ1出力の 3 テキストから ``ExtractedHearingBundle`` を組み立てる。"""
    d = phase1_dir.resolve()
    for name in ("hearing_sheet_content.txt", "appo_memo.txt", "sales_notes.txt"):
        if not (d / name).is_file():
            raise FileNotFoundError(f"フェーズ1スナップショットに {name} がありません: {d}")
    return ExtractedHearingBundle(
        hearing_sheet_content=(d / "hearing_sheet_content.txt").read_text(encoding="utf-8"),
        appo_memo=(d / "appo_memo.txt").read_text(encoding="utf-8"),
        sales_notes=(d / "sales_notes.txt").read_text(encoding="utf-8"),
    )


def load_phase1_case_meta(phase1_dir: Path) -> dict[str, Any]:
    p = phase1_dir.resolve() / "01_case_meta.json"
    if not p.is_file():
        raise FileNotFoundError(f"01_case_meta.json がありません: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("01_case_meta.json はオブジェクトである必要があります")
    return data


def contract_work_branch_from_final_field(value: object) -> ContractWorkBranch:
    """``work_branch_snapshots`` の ``branch_final`` 等の文字列を列挙に変換する。"""
    key = str(value or "").strip().lower()
    for b in ContractWorkBranch:
        if b.value == key:
            return b
    raise ValueError(f"branch_final が ContractWorkBranch と一致しません: {value!r}")


def find_work_branch_row_for_record(
    work_branches_json: Path,
    record_number: str,
) -> dict[str, Any] | None:
    """``01_work_branches.json`` から ``record_number`` が一致する行を返す。"""
    p = work_branches_json.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"work_branches JSON が見つかりません: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"JSON はリストである必要があります: {p}")
    rn = str(record_number).strip()
    for row in raw:
        if not isinstance(row, dict):
            continue
        if str(row.get("record_number") or "").strip() == rn:
            return row
    return None


def infer_latest_work_branches_json(phase1_dir: Path) -> Path | None:
    """
    ``<run_root>/phase1_snapshots/<stamp>/`` から ``run_root`` を推定し、
    最新の ``work_branch_snapshots/*/01_work_branches.json`` を返す。
    """
    run_root = phase1_dir.resolve().parent.parent
    base = run_root / "work_branch_snapshots"
    if not base.is_dir():
        return None
    candidates = list(base.glob("*/01_work_branches.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda x: x.stat().st_mtime)


def resolve_work_branch_for_phase2_replay(
    meta: dict[str, Any],
    *,
    work_branches_json: Path | None,
    use_spreadsheet_when_no_wb_row: bool,
) -> tuple[ContractWorkBranch, str]:
    """
    作業分岐を決める。

    Returns:
        (branch, source) — source は ``work_branch_json`` / ``spreadsheet`` / ``contract_plan_only``
    """
    plan = str(meta.get("contract_plan") or "")
    record_number = str(meta.get("record_number") or "")
    partner_name = str(meta.get("partner_name") or "")

    if work_branches_json is not None:
        row = find_work_branch_row_for_record(work_branches_json, record_number)
        if row is not None and row.get("branch_final") is not None:
            return (
                contract_work_branch_from_final_field(row["branch_final"]),
                "work_branch_json",
            )
        logger.warning(
            "work_branches_json に record_number=%s の行が無いか branch_final がありません。"
            " フォールバックします。",
            record_number,
        )

    if use_spreadsheet_when_no_wb_row:
        sheet = SpreadsheetClient()
        return (
            resolve_work_branch_with_basic_lp_override(
                plan,
                record_number=record_number,
                partner_name=partner_name,
                lookup_basic_is_landing_page=sheet.lookup_basic_is_landing_page,
            ),
            "spreadsheet",
        )

    return (resolve_contract_work_branch(plan), "contract_plan_only")


def snapshot_phase2_text_llm_from_phase1_dir(
    phase1_dir: Path,
    *,
    work_branches_json: Path | None = None,
    use_spreadsheet_when_no_wb_row: bool = False,
    output_root: Path | None = None,
    explicit_run_root: Path | None = None,
) -> Path:
    """
    フェーズ1ディレクトリを入力に ``run_text_llm_stage`` を実行し、成果を保存する。

    Args:
        phase1_dir: ``phase1_snapshots/<UTC>/``
        work_branches_json: 省略時は ``infer_latest_work_branches_json`` を試す
        use_spreadsheet_when_no_wb_row: True のとき、JSON に行が無ければ Sheets で BASIC_LP 判定
        output_root: ``phase2_snapshots`` 相当（未指定は ``pipeline_phase2_snapshots_base``）
        explicit_run_root: ``output_root`` 未指定時の run 親（PIPELINE_TEST_RUN_DIR と同様）

    Returns:
        保存先ディレクトリ
    """
    bundle = load_hearing_bundle_from_phase1_dir(phase1_dir)
    meta = load_phase1_case_meta(phase1_dir)
    plan = str(meta.get("contract_plan") or "")
    partner_name = str(meta.get("partner_name") or "")
    record_number = str(meta.get("record_number") or "")

    wb_path = work_branches_json
    if wb_path is None:
        wb_path = infer_latest_work_branches_json(phase1_dir)

    branch, branch_source = resolve_work_branch_for_phase2_replay(
        meta,
        work_branches_json=wb_path,
        use_spreadsheet_when_no_wb_row=use_spreadsheet_when_no_wb_row,
    )

    base = output_root or pipeline_phase2_snapshots_base(explicit_run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    _write_json(
        out / "00_source.json",
        {
            "phase1_dir": str(phase1_dir.resolve()),
            "work_branches_json": str(wb_path.resolve()) if wb_path else None,
            "branch_resolution": branch_source,
            "work_branch": branch.value,
        },
    )
    _write_json(out / "01_case_meta.json", meta)

    requirements_result, spec = run_text_llm_stage(
        bundle,
        contract_plan=plan,
        partner_name=partner_name,
        record_number=record_number,
        work_branch=branch,
    )

    write_llm_yaml_artifact(out / "requirements_result.yaml", requirements_result)
    write_llm_yaml_artifact(out / "spec.yaml", spec)
    write_llm_yaml_artifact(
        out / "02_summary.yaml",
        {
            "work_branch": branch.value,
            "branch_resolution": branch_source,
            "hearing_sheet_content_chars": len(bundle.hearing_sheet_content or ""),
            "requirements_result_keys": sorted(requirements_result.keys()),
            "spec_top_keys": sorted(spec.keys()) if isinstance(spec, dict) else None,
        },
    )

    (out / "README.txt").write_text(
        "\n".join(
            [
                "フェーズ2スナップショット（run_text_llm_stage）",
                "",
                "00_source.json — phase1 入力・work_branches JSON・作業分岐の解決方法",
                "01_case_meta.json — フェーズ1からのコピー",
                "requirements_result.yaml — TEXT_LLM の要望側出力（UTF-8 テキスト）",
                "spec.yaml — サイト生成向け仕様（UTF-8 テキスト）",
                "02_summary.yaml — 文字数・キー一覧（ざっくり確認用・テキスト）",
                "",
            ]
        ),
        encoding="utf-8",
    )
    logger.info("フェーズ2スナップショット保存: %s", out)
    return out


def main_argv(argv: list[str] | None = None) -> None:
    import argparse

    from config.logging_setup import configure_logging

    configure_logging()

    parser = argparse.ArgumentParser(
        description="フェーズ1スナップショットを入力に TEXT_LLM（フェーズ2）を実行して保存"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/（省略時は最新 phase1_snapshots を探索）",
    )
    parser.add_argument(
        "--work-branches-json",
        type=Path,
        default=None,
        metavar="PATH",
        help="work_branch_snapshots/*/01_work_branches.json（省略時は phase1 と同じ run 配下の最新を使用）",
    )
    parser.add_argument(
        "--no-infer-work-branches",
        action="store_true",
        help="work_branches JSON の自動推定をしない（契約プラン列のみで分岐）",
    )
    parser.add_argument(
        "--use-spreadsheet-fallback",
        action="store_true",
        help=(
            "work_branches JSON に当該レコードが無いとき、本番と同様にサイトタイプシートで "
            "BASIC→BASIC_LP を判定する（要認証。付けないと契約列が BASIC でも常に BASIC-CP 側になる）"
        ),
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="1 ラン用の親（phase2_snapshots の保存先の親。省略時は phase1 と同じ run または OUTPUT_DIR）",
    )
    args = parser.parse_args(argv)

    rr = args.run_dir.resolve() if args.run_dir else None

    phase1: Path
    if args.phase1_dir:
        phase1 = args.phase1_dir.resolve()
    else:
        found = latest_phase1_snapshot_dir(run_root=rr)
        if found is None:
            print(
                "ERROR: --phase1-dir 未指定かつ phase1_snapshots が見つかりません",
                file=sys.stderr,
            )
            sys.exit(1)
        phase1 = found
        print(f"入力（最新フェーズ1）: {phase1}")

    if rr is None:
        p = phase1.resolve()
        if p.parent.name == "phase1_snapshots":
            rr = p.parent.parent

    wb_json: Path | None = None
    if args.work_branches_json:
        wb_json = args.work_branches_json.resolve()
    elif not args.no_infer_work_branches:
        inferred = infer_latest_work_branches_json(phase1)
        if inferred is not None:
            wb_json = inferred
            print(f"入力（推定 work_branches）: {wb_json}")

    out = snapshot_phase2_text_llm_from_phase1_dir(
        phase1,
        work_branches_json=wb_json,
        use_spreadsheet_when_no_wb_row=args.use_spreadsheet_fallback,
        explicit_run_root=rr,
    )
    print(f"保存先: {out}")


if __name__ == "__main__":
    main_argv()
