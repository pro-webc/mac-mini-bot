#!/usr/bin/env python3
"""
フェーズ1スナップショットを入力に、STANDARD-CP の Gemini **1/15（手順1-1・タブ①）**だけ実行する。

  python3 scripts/gemini_standard_cp_step1_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC>

成果物は **他の工程テストと同じ run 配下**の ``gemini_step_tests/<UTC>/`` に保存する
（``phase1_snapshots`` の親が ``<run>`` とみなせるときは ``--run-dir`` 省略可）。

  python3 scripts/gemini_standard_cp_step1_from_phase1.py \\
    --phase1-dir ... --run-dir output/pipeline_test_runs/<run>

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
from modules.phase2_text_llm_snapshot import load_hearing_bundle_from_phase1_dir  # noqa: E402
from modules.standard_cp_gemini_manual import run_standard_cp_gemini_api_call_1_of_15  # noqa: E402


def _resolve_run_root(*, phase1: Path, run_dir: Path | None) -> Path:
    if run_dir is not None:
        return run_dir.resolve()
    inferred = pipeline_run_root_from_phase1_snapshot_dir(phase1)
    if inferred is not None:
        return inferred
    print(
        "ERROR: phase1 が .../phase1_snapshots/<UTC>/ 配下に無いときは "
        "--run-dir で pipeline_test_runs/<run>（または PIPELINE_TEST_RUN_DIR と同じ親）を指定してください。",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Gemini 1/15（手順1-1）をフェーズ1入力で実行"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="1 ラン用の親（preflight / phase1 と並ぶディレクトリ）。省略時は phase1 の親の親を使用",
    )
    args = parser.parse_args()

    phase1 = args.phase1_dir.resolve()
    run_root = _resolve_run_root(phase1=phase1, run_dir=args.run_dir)

    bundle = load_hearing_bundle_from_phase1_dir(phase1)
    h = bundle.hearing_sheet_content or ""

    prompt, response = run_standard_cp_gemini_api_call_1_of_15(hearing_sheet_content=h)

    base = pipeline_gemini_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)
    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_1_1.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_1_1.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_1_1",
        "gemini_call_index_1based": 1,
        "gemini_calls_total_standard_cp": 15,
        "hearing_sheet_content_chars": len(h),
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
                "STANDARD-CP Gemini 段階テスト（手順1-1・API 1/15）",
                "",
                "00_source.json — phase1 入力ディレクトリ・run 親",
                "01_prompt_step_1_1.txt — Gemini に渡したプロンプト",
                "02_response_step_1_1.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 1/15（手順1-1）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"HEARING_BLOCK: {len(h)} 文字 / プロンプト: {len(prompt)} / 応答: {len(response)}")


if __name__ == "__main__":
    main()
