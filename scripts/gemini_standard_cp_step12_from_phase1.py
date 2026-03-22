#!/usr/bin/env python3
"""
**11回目の成果物**（手順6 の応答 ``02_response_step_6.txt``）を ``STEP_6_OUTPUT`` に埋め込み、
STANDARD-CP の Gemini **12/15（手順7-1・タブ⑥・新規チャット）**だけ実行する。

::

  python3 scripts/gemini_standard_cp_step12_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-gemini-dir output/pipeline_test_runs/<run>/gemini_step_tests/<11回目UTC>

成果物は **同じ run 配下**の ``gemini_step_tests/<新UTC>/`` に保存。

リポジトリルートで実行。
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

from config.config import (  # noqa: E402
    pipeline_gemini_step_tests_base,
    pipeline_run_root_from_phase1_snapshot_dir,
)
from modules.standard_cp_gemini_manual import run_standard_cp_gemini_api_call_12_of_15  # noqa: E402


def _resolve_run_root(*, phase1: Path, run_dir: Path | None) -> Path:
    if run_dir is not None:
        return run_dir.resolve()
    inferred = pipeline_run_root_from_phase1_snapshot_dir(phase1)
    if inferred is not None:
        return inferred
    print(
        "ERROR: phase1 が .../phase1_snapshots/<UTC>/ 配下に無いときは "
        "--run-dir で pipeline_test_runs/<run> を指定してください。",
        file=sys.stderr,
    )
    sys.exit(1)


def _load_step6_response(prev_dir: Path) -> str:
    d = prev_dir.resolve()
    p = d / "02_response_step_6.txt"
    if not p.is_file():
        print(
            f"ERROR: {p} がありません（--prev-gemini-dir は11回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Gemini 12/15（手順7-1・タブ⑥・新規チャット）"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/（run 親の推定用）",
    )
    parser.add_argument(
        "--prev-gemini-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="11回目テストの出力（02_response_step_6.txt）",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="1 ラン用の親。省略時は phase1 から推定",
    )
    args = parser.parse_args()

    phase1 = args.phase1_dir.resolve()
    run_root = _resolve_run_root(phase1=phase1, run_dir=args.run_dir)
    prev11 = args.prev_gemini_dir.resolve()
    r6 = _load_step6_response(prev11)

    prompt, response = run_standard_cp_gemini_api_call_12_of_15(step_6_output=r6)

    base = pipeline_gemini_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_gemini_dir": str(prev11),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_7_1.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_7_1.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_7_1",
        "gemini_call_index_1based": 12,
        "gemini_calls_total_standard_cp": 15,
        "prompt_chars": len(prompt),
        "response_chars": len(response),
    }
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "README.txt").write_text(
        "\n".join(
            [
                "STANDARD-CP Gemini 段階テスト（手順7-1・API 12/15・タブ⑥1通目）",
                "",
                "00_source.json — phase1・run・11回目参照",
                "01_prompt_step_7_1.txt — step_7_1.txt 置換済み",
                "02_response_step_7_1.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ 手順6応答を STEP_6_OUTPUT に埋め込み、新規チャットで送信。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 12/15（手順7-1・タブ⑥）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
