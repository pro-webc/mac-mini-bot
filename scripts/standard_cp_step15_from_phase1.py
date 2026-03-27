#!/usr/bin/env python3
"""
**15回目**（手順7-4）のプロンプト＋応答と、``00_source.json`` チェーンで辿れる **14→13→12回目**
（手順7-3・7-2・7-1）を読み込みタブ⑥を4往復復元し、STANDARD-CP の Claude **16/16（手順7-5・最終仕上げ）**だけ実行する。

``--prev-step-dir`` は **15回目**フォルダ（``01_prompt_step_7_4.txt`` 等と ``00_source.json``）。

::

  python3 scripts/standard_cp_step15_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<15回目UTC>

成果物は **同じ run 配下**の ``claude_step_tests/<新UTC>/`` に保存。

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
    pipeline_claude_step_tests_base,
    pipeline_run_root_from_phase1_snapshot_dir,
)
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_16_of_16  # noqa: E402


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


def _load_src(prev: Path) -> dict:
    p = prev.resolve() / "00_source.json"
    if not p.is_file():
        print(f"ERROR: {p} がありません。", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def _load_7_1_turn(d: Path) -> tuple[str, str]:
    x = d.resolve()
    a, b = x / "01_prompt_step_7_1.txt", x / "02_response_step_7_1.txt"
    if not a.is_file() or not b.is_file():
        print(f"ERROR: {x} に手順7-1の保存がありません。", file=sys.stderr)
        sys.exit(1)
    return a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")


def _load_7_2_turn(d: Path) -> tuple[str, str]:
    x = d.resolve()
    a, b = x / "01_prompt_step_7_2.txt", x / "02_response_step_7_2.txt"
    if not a.is_file() or not b.is_file():
        print(f"ERROR: {x} に手順7-2の保存がありません。", file=sys.stderr)
        sys.exit(1)
    return a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")


def _load_7_3_turn(d: Path) -> tuple[str, str]:
    x = d.resolve()
    a, b = x / "01_prompt_step_7_3.txt", x / "02_response_step_7_3.txt"
    if not a.is_file() or not b.is_file():
        print(f"ERROR: {x} に手順7-3の保存がありません。", file=sys.stderr)
        sys.exit(1)
    return a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")


def _load_7_4_turn(d: Path) -> tuple[str, str]:
    x = d.resolve()
    a, b = x / "01_prompt_step_7_4.txt", x / "02_response_step_7_4.txt"
    if not a.is_file() or not b.is_file():
        print(f"ERROR: {x} に手順7-4の保存がありません。", file=sys.stderr)
        sys.exit(1)
    return a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 16/16（手順7-5・タブ⑥5通目・最終仕上げ）"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/（run 親の推定用）",
    )
    parser.add_argument(
        "--prev-step-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="15回目テストの出力（手順7-4）。00_source で14→13→12を辿る",
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
    d15 = args.prev_step_dir.resolve()
    p74, r74 = _load_7_4_turn(d15)

    src15 = _load_src(d15)
    prev14 = src15.get("prev_step_dir")
    if not prev14:
        print("ERROR: 15回目 00_source.json に prev_step_dir がありません。", file=sys.stderr)
        sys.exit(1)
    d14 = Path(prev14)
    p73, r73 = _load_7_3_turn(d14)

    src14 = _load_src(d14)
    prev13 = src14.get("prev_step_dir")
    if not prev13:
        print("ERROR: 14回目 00_source.json に prev_step_dir がありません。", file=sys.stderr)
        sys.exit(1)
    d13 = Path(prev13)
    p72, r72 = _load_7_2_turn(d13)

    src13 = _load_src(d13)
    prev12 = src13.get("prev_step_dir")
    if not prev12:
        print("ERROR: 13回目 00_source.json に prev_step_dir がありません。", file=sys.stderr)
        sys.exit(1)
    d12 = Path(prev12)
    p71, r71 = _load_7_1_turn(d12)

    prompt, response = run_standard_cp_claude_api_call_16_of_16(
        step_7_1_prompt=p71,
        step_7_1_response=r71,
        step_7_2_prompt=p72,
        step_7_2_response=r72,
        step_7_3_prompt=p73,
        step_7_3_response=r73,
        step_7_4_prompt=p74,
        step_7_4_response=r74,
    )

    base = pipeline_claude_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_step_dir": str(d15),
                "step14_dir": str(d14.resolve()),
                "step13_dir": str(d13.resolve()),
                "step12_dir": str(d12.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_7_5.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_7_5.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_7_5",
        "claude_call_index_1based": 16,
        "claude_calls_total_standard_cp": 16,
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
                "STANDARD-CP Claude 段階テスト（手順7-5・API 16/16・タブ⑥5通目・最終仕上げ）",
                "",
                "00_source.json — phase1・run・15/14/13/12 回目参照",
                "01_prompt_step_7_5.txt — step_7_5.txt 本文",
                "02_response_step_7_5.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は手順7-1〜7-4で start_chat(history) を4往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 16/16（手順7-5・タブ⑥5通目・最終仕上げ）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
