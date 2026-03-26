#!/usr/bin/env python3
"""
**4回目の成果物**（手順3-1 のプロンプト＋応答）を入力に、STANDARD-CP の Claude **5/15（手順3-2・タブ④の2通目）**だけ実行する。

本番と同じ **同一チャット** のため、``01_prompt_step_3_1.txt`` と ``02_response_step_3_1.txt`` で履歴を復元してから手順3-2 を送る。

4回目のフォルダを ``--prev-step-dir`` で渡す::

  python3 scripts/standard_cp_step5_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<4回目UTC>

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_5_of_15  # noqa: E402


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


def _load_step3_1_turn(prev_dir: Path) -> tuple[str, str]:
    d = prev_dir.resolve()
    p_prompt = d / "01_prompt_step_3_1.txt"
    p_resp = d / "02_response_step_3_1.txt"
    if not p_prompt.is_file():
        print(
            f"ERROR: {p_prompt} がありません（--prev-step-dir は4回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_resp.is_file():
        print(
            f"ERROR: {p_resp} がありません（--prev-step-dir は4回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_prompt.read_text(encoding="utf-8"), p_resp.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 5/15（手順3-2・タブ④2通目・チャット継続）"
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
        help="4回目テストの出力（01_prompt_step_3_1.txt・02_response_step_3_1.txt を含む）",
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
    prev = args.prev_step_dir.resolve()

    p31, r31 = _load_step3_1_turn(prev)
    prompt, response = run_standard_cp_claude_api_call_5_of_15(
        step_3_1_prompt=p31,
        step_3_1_response=r31,
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
                "prev_step_dir": str(prev),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_3_2.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_3_2.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_3_2",
        "claude_call_index_1based": 5,
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
                "STANDARD-CP Claude 段階テスト（手順3-2・API 5/15・タブ④2通目）",
                "",
                "00_source.json — phase1・run・4回目参照",
                "01_prompt_step_3_2.txt — step_3_2.txt 本文（置換なし）",
                "02_response_step_3_2.txt — 応答（サービスページ案など）",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は 4回目の 3-1 プロンプト/応答で start_chat(history) を復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 5/15（手順3-2・タブ④2通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
