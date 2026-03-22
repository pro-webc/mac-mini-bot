#!/usr/bin/env python3
"""
本番 WebsiteBot.run() と同じ起動〜キュー切り詰め〜process_case 直前までを1回実行し、
output/preflight_snapshots/<UTC時刻>/ に保存する。

  python3 scripts/preflight_before_process_case.py

本番で 1 件だけ動かす検証（main と同じキュー）に合わせる場合:

    BOT_MAX_CASES=1 python3 scripts/preflight_before_process_case.py

1 ラン用フォルダ配下に出す（``pipeline_test_snapshots.py`` と同じレイアウト）:

    python3 scripts/preflight_before_process_case.py --run-dir output/pipeline_test_runs/my_run

リポジトリルートで実行すること（.env・仮想環境は main と同じ前提）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.config import pipeline_preflight_snapshots_base
from modules.pipeline_preflight_snapshot import snapshot_preflight_before_process_case


def main() -> None:
    parser = argparse.ArgumentParser(
        description="preflight スナップショット（process_case 直前まで）"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="親ディレクトリ（その下に preflight_snapshots/<UTC>/ を作成）",
    )
    args = parser.parse_args()
    rr = args.run_dir.resolve() if args.run_dir else None
    out = snapshot_preflight_before_process_case(
        output_root=pipeline_preflight_snapshots_base(rr),
    )
    print(f"保存先: {out}")


if __name__ == "__main__":
    main()
