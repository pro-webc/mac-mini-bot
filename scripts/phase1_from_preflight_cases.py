#!/usr/bin/env python3
"""
プリフライトの ``04_pending_cases.json`` を入力に、フェーズ1（ヒアリング抽出）だけ実行して保存する。

  python3 scripts/phase1_from_preflight_cases.py [04_pending_cases.json] [--case-index N]

引数省略時は ``output/preflight_snapshots`` 内の最新 ``04_pending_cases.json`` を使う
（または環境変数 ``PIPELINE_TEST_RUN_DIR`` / ``--run-dir`` で指定した親の ``preflight_snapshots``）。

1 ラン用フォルダに出す例::

    python3 scripts/phase1_from_preflight_cases.py --run-dir output/pipeline_test_runs/my_run

連続実行は ``scripts/pipeline_test_snapshots.py`` を参照。

成果物は hearing_sheet_content.txt など UTF-8 テキスト（コピペ用）と要約 JSON。

リポジトリルートで実行（.env・認証は main と同じ前提。fetch_hearing_sheet が URL 取得する場合はネットワーク使用）。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.phase1_hearing_snapshot import main_argv


if __name__ == "__main__":
    main_argv()
