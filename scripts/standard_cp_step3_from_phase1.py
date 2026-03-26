#!/usr/bin/env python3
"""
**2回目の応答**（手順1-3 相当の長文）を入力に、STANDARD-CP の Claude **3/15（手順2・タブ③）**だけ実行する。

2回目の成果物フォルダ（``02_response_step_1_2_and_1_3.txt`` があるディレクトリ）を ``--prev-step-dir`` で渡す::

  python3 scripts/standard_cp_step3_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<2回目UTC>

応答テキストだけ別ファイルにある場合は ``--step1-3-response`` で指定。

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_3_of_15  # noqa: E402


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


def _load_step1_3_response(prev_dir: Path | None, response_file: Path | None) -> str:
    if response_file is not None:
        p = response_file.resolve()
        if not p.is_file():
            print(f"ERROR: --step1-3-response が見つかりません: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8")
    if prev_dir is None:
        print(
            "ERROR: --prev-step-dir か --step1-3-response のどちらかが必要です。",
            file=sys.stderr,
        )
        sys.exit(1)
    d = prev_dir.resolve()
    inner = d / "02_response_step_1_2_and_1_3.txt"
    if not inner.is_file():
        print(
            f"ERROR: {inner} がありません（--prev-step-dir は2回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return inner.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 3/15（手順2・タブ③）を手順1-3応答で実行"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/（run 親の推定用）",
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--prev-step-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="2回目テストの出力（02_response_step_1_2_and_1_3.txt を含む）",
    )
    g.add_argument(
        "--step1-3-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順1-3 相当の応答テキストファイル（タブ②の連結応答）",
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

    step13 = _load_step1_3_response(args.prev_step_dir, args.step1_3_response)

    prompt, response = run_standard_cp_claude_api_call_3_of_15(step_1_3_output=step13)

    base = pipeline_claude_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    prev_ref: str | None = None
    if args.prev_step_dir is not None:
        prev_ref = str(args.prev_step_dir.resolve())
    step13_file: str | None = None
    if args.step1_3_response is not None:
        step13_file = str(args.step1_3_response.resolve())

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_step_dir": prev_ref,
                "step1_3_response_file": step13_file,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_2.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_2.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_2",
        "claude_call_index_1based": 3,
        "claude_calls_total_standard_cp": 15,
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
                "STANDARD-CP Claude 段階テスト（手順2・API 3/15・タブ③）",
                "",
                "00_source.json — phase1・run・2回目参照",
                "01_prompt_step_2.txt — step_2.txt 置換済みプロンプト",
                "02_response_step_2.txt — 応答（6ページ構成案など）",
                "meta.json — 文字数・メタ",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 3/15（手順2・タブ③）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
