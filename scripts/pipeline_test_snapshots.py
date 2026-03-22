#!/usr/bin/env python3
"""
プリフライト → フェーズ1 → 作業分岐スナップショットを **1 つの親ディレクトリ** にまとめて保存する。

  python3 scripts/pipeline_test_snapshots.py
  python3 scripts/pipeline_test_snapshots.py --run-dir output/pipeline_test_runs/my_run

第1引数なしのときは ``output/pipeline_test_runs/<UTC>/`` を新規作成する。
その直下に ``preflight_snapshots/``, ``phase1_snapshots/``, ``work_branch_snapshots/`` が並ぶ。

本番と同じキュー長に揃える例::

    BOT_MAX_CASES=1 python3 scripts/pipeline_test_snapshots.py

リポジトリルートで実行（.env・認証は main と同じ前提）。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.config import (
    OUTPUT_DIR,
    pipeline_phase1_snapshots_base,
    pipeline_preflight_snapshots_base,
    pipeline_work_branch_snapshots_base,
)
from modules.phase1_hearing_snapshot import snapshot_phase1_from_cases_json
from modules.pipeline_preflight_snapshot import snapshot_preflight_before_process_case
from modules.work_branch_snapshot import (
    cases_json_path_from_phase1_snapshot_dir,
    snapshot_work_branches_from_cases_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="プリフライト・フェーズ1・作業分岐を同一 run-dir に保存"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="親ディレクトリ（省略時は output/pipeline_test_runs/<UTC>/ を作成）",
    )
    parser.add_argument(
        "--case-index",
        type=int,
        default=0,
        help="フェーズ1で 04 の何件目を使うか（既定: 0）",
    )
    args = parser.parse_args()
    if args.run_dir:
        run_root = args.run_dir.resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_root = (OUTPUT_DIR / "pipeline_test_runs" / stamp).resolve()
    run_root.mkdir(parents=True, exist_ok=True)

    print(f"run ディレクトリ: {run_root}")
    pref_out = snapshot_preflight_before_process_case(
        output_root=pipeline_preflight_snapshots_base(run_root),
    )
    print(f"preflight: {pref_out}")
    cases = pref_out / "04_pending_cases.json"
    phase1_out = snapshot_phase1_from_cases_json(
        cases,
        case_index=args.case_index,
        output_root=pipeline_phase1_snapshots_base(run_root),
    )
    print(f"phase1: {phase1_out}")
    case_path = cases_json_path_from_phase1_snapshot_dir(phase1_out)
    wb_out = snapshot_work_branches_from_cases_json(
        case_path,
        output_root=pipeline_work_branch_snapshots_base(run_root),
        phase1_snapshot_dir=phase1_out,
    )
    print(f"work_branch: {wb_out}")

    manifest = {
        "run_root": str(run_root),
        "preflight_snapshot": str(pref_out),
        "phase1_snapshot": str(phase1_out),
        "work_branch_snapshot": str(wb_out),
        "cases_json": str(case_path),
    }
    (run_root / "00_pipeline_test_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_root / "README.txt").write_text(
        "\n".join(
            [
                "工程テストスナップショット（1 ラン分）",
                "",
                "preflight_snapshots/ — WebsiteBot 直前まで（04 = キュー）",
                "phase1_snapshots/ — ヒアリング抽出",
                "work_branch_snapshots/ — 契約プラン作業分岐",
                "",
                "TEXT_LLM 単体: scripts/phase2_from_phase1_snapshot.py（phase1 + 任意で work_branch JSON）",
                "gemini_step_tests/ — gemini_standard_cp_step1〜10_from_phase1.py（1〜10/15・"
                "タブ⑤手順5まで段階化・step7は3-4で本番手順7-1と別）",
                "",
                "00_pipeline_test_manifest.json に各タイムスタンプ付きディレクトリのパスを記録。",
                "",
                "フォルダ・ファイルの読み方: PIPELINE_TESTING.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"マニフェスト: {run_root / '00_pipeline_test_manifest.json'}")


if __name__ == "__main__":
    main()
