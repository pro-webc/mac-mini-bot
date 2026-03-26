#!/usr/bin/env python3
"""
**9回目の成果物**（手順4 のプロンプト＋応答）でタブ⑤チャットを復元し、
**2回目・3回目**の応答から **手順1-3 本文**と**手順2 本文**を読み込んで、
STANDARD-CP の Claude **10/15（手順5・タブ⑤の2通目）**だけ実行する。

::

  python3 scripts/standard_cp_step10_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<9回目UTC> \\
    --step1-3-dir output/pipeline_test_runs/<run>/claude_step_tests/<2回目UTC> \\
    --step2-dir output/pipeline_test_runs/<run>/claude_step_tests/<3回目UTC>

応答テキストをファイルで渡す場合は ``--step1-3-response`` / ``--step2-response`` を **両方**指定（ディレクトリ指定と混在不可）。

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_10_of_15  # noqa: E402


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


def _load_step4_turn(prev_dir: Path) -> tuple[str, str]:
    d = prev_dir.resolve()
    p_prompt = d / "01_prompt_step_4.txt"
    p_resp = d / "02_response_step_4.txt"
    if not p_prompt.is_file():
        print(
            f"ERROR: {p_prompt} がありません（--prev-step-dir は9回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_resp.is_file():
        print(
            f"ERROR: {p_resp} がありません（--prev-step-dir は9回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_prompt.read_text(encoding="utf-8"), p_resp.read_text(encoding="utf-8")


def _load_step1_3_from_dir(d: Path) -> str:
    p = d.resolve() / "02_response_step_1_2_and_1_3.txt"
    if not p.is_file():
        print(
            f"ERROR: {p} がありません（--step1-3-dir は2回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _load_step2_from_dir(d: Path) -> str:
    p = d.resolve() / "02_response_step_2.txt"
    if not p.is_file():
        print(
            f"ERROR: {p} がありません（--step2-dir は3回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _load_text_file(path: Path, label: str) -> str:
    p = path.resolve()
    if not p.is_file():
        print(f"ERROR: {label} が見つかりません: {p}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 10/15（手順5・タブ⑤2通目・チャット継続）"
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
        help="9回目テストの出力（01_prompt_step_4.txt・02_response_step_4.txt）",
    )
    parser.add_argument(
        "--step1-3-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="2回目フォルダ（02_response_step_1_2_and_1_3.txt を含む）。--step1-3-response とは排他",
    )
    parser.add_argument(
        "--step2-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="3回目フォルダ（02_response_step_2.txt を含む）。--step2-response とは排他",
    )
    parser.add_argument(
        "--step1-3-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順1-3 相当の応答テキストファイル。--step2-response とセットで指定",
    )
    parser.add_argument(
        "--step2-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順2 相当の応答テキストファイル。--step1-3-response とセットで指定",
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
    prev9 = args.prev_step_dir.resolve()

    p4, r4 = _load_step4_turn(prev9)

    has_dirs = args.step1_3_dir is not None and args.step2_dir is not None
    has_files = args.step1_3_response is not None and args.step2_response is not None
    partial_dir = (args.step1_3_dir is not None) ^ (args.step2_dir is not None)
    partial_file = (args.step1_3_response is not None) ^ (args.step2_response is not None)

    if partial_dir or partial_file:
        print(
            "ERROR: --step1-3-dir と --step2-dir は両方、または "
            "--step1-3-response と --step2-response は両方指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    if has_dirs and has_files:
        print(
            "ERROR: ディレクトリ指定とファイル指定は同時に使えません。",
            file=sys.stderr,
        )
        sys.exit(1)
    if not has_dirs and not has_files:
        print(
            "ERROR: (--step1-3-dir と --step2-dir) または "
            "(--step1-3-response と --step2-response) が必要です。",
            file=sys.stderr,
        )
        sys.exit(1)

    if has_dirs:
        step13 = _load_step1_3_from_dir(args.step1_3_dir)
        step2 = _load_step2_from_dir(args.step2_dir)
        step13_ref = str(args.step1_3_dir.resolve())
        step2_ref = str(args.step2_dir.resolve())
    else:
        step13 = _load_text_file(
            args.step1_3_response, "--step1-3-response"
        )
        step2 = _load_text_file(args.step2_response, "--step2-response")
        step13_ref = str(args.step1_3_response.resolve())
        step2_ref = str(args.step2_response.resolve())

    prompt, response = run_standard_cp_claude_api_call_10_of_15(
        step_4_prompt=p4,
        step_4_response=r4,
        step_1_3_output=step13,
        step_2_output=step2,
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
                "prev_step_dir": str(prev9),
                "step1_3_source": step13_ref,
                "step2_source": step2_ref,
                "step1_3_via_files": not has_dirs,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_5.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_5.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_5",
        "claude_call_index_1based": 10,
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
                "STANDARD-CP Claude 段階テスト（手順5・API 10/15・タブ⑤2通目）",
                "",
                "00_source.json — phase1・run・9回目・2/3回目参照",
                "01_prompt_step_5.txt — step_5.txt 置換済み",
                "02_response_step_5.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は9回目の手順4で start_chat(history) を1往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 10/15（手順5・タブ⑤2通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
