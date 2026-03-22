#!/usr/bin/env python3
"""
フェーズ1スナップショット（工程テストの成果物）を入力に TEXT_LLM（フェーズ2）だけ実行する。

  python3 scripts/phase2_from_phase1_snapshot.py --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC>/

同じ run 配下に ``work_branch_snapshots/*/01_work_branches.json`` があれば自動で読み、
``record_number`` が一致する行の ``branch_final`` で作業分岐を再現する（本番の BASIC_LP 寄せと揃える）。

省略例（最新の phase1 を探索・成果は同じ run 直下の ``phase2_snapshots/`` へ）::

  python3 scripts/phase2_from_phase1_snapshot.py --run-dir output/pipeline_test_runs/<run>

環境変数・Gemini 有効化は本番 ``main.py`` と同じ（各 ``*_USE_GEMINI_MANUAL`` / ``GEMINI_API_KEY``）。

リポジトリルートで実行。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.phase2_text_llm_snapshot import main_argv  # noqa: E402

if __name__ == "__main__":
    main_argv()
