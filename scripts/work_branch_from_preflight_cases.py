#!/usr/bin/env python3
"""
プリフライトの ``04_pending_cases.json`` を入力に、契約プラン作業分岐（main.process_case と同じ）を算出して保存する。

  python3 scripts/work_branch_from_preflight_cases.py [04_pending_cases.json]

引数省略時は ``output/preflight_snapshots`` 内の最新 ``04_pending_cases.json``
（または ``PIPELINE_TEST_RUN_DIR`` / ``--run-dir`` 配下の最新）。

フェーズ1の結果を入力にする（``00_source.json`` の ``cases_json`` を使う）:

  python3 scripts/work_branch_from_preflight_cases.py --from-phase1 output/phase1_snapshots/<UTC>/
  python3 scripts/work_branch_from_preflight_cases.py --from-phase1

1 ラン用フォルダ（``--run-dir``）では、その下の ``phase1_snapshots`` / ``preflight_snapshots`` を参照します。
まとめて実行する場合は ``scripts/pipeline_test_snapshots.py``。

BASIC 行は ``lookup_basic_is_landing_page`` で Sheets API を参照する。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.work_branch_snapshot import main_argv


if __name__ == "__main__":
    main_argv()
