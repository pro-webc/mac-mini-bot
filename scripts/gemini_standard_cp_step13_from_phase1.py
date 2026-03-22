#!/usr/bin/env python3
"""
**12回目の成果物**（手順7-1 のプロンプト＋応答）でタブ⑥を1往復復元し、
**4回目**の手順3-1応答・**3回目**の手順2応答を読み込んで ``step_7_2.txt`` を置換し、
STANDARD-CP の Gemini **13/15（手順7-2・タブ⑥の2通目）**だけ実行する。

::

  python3 scripts/gemini_standard_cp_step13_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-gemini-dir output/pipeline_test_runs/<run>/gemini_step_tests/<12回目UTC> \\
    --step3-1-dir output/pipeline_test_runs/<run>/gemini_step_tests/<4回目UTC> \\
    --step2-dir output/pipeline_test_runs/<run>/gemini_step_tests/<3回目UTC>

応答テキストをファイルで渡す場合は ``--step3-1-response`` / ``--step2-response`` を **両方**
指定（ディレクトリ指定と混在不可）。

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
from modules.standard_cp_gemini_manual import run_standard_cp_gemini_api_call_13_of_15  # noqa: E402


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


def _load_step7_1_turn(prev_dir: Path) -> tuple[str, str]:
    d = prev_dir.resolve()
    p_p = d / "01_prompt_step_7_1.txt"
    p_r = d / "02_response_step_7_1.txt"
    if not p_p.is_file():
        print(
            f"ERROR: {p_p} がありません（--prev-gemini-dir は12回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_r.is_file():
        print(
            f"ERROR: {p_r} がありません（--prev-gemini-dir は12回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_p.read_text(encoding="utf-8"), p_r.read_text(encoding="utf-8")


def _load_step3_1_from_dir(d: Path) -> str:
    p = d.resolve() / "02_response_step_3_1.txt"
    if not p.is_file():
        print(
            f"ERROR: {p} がありません（--step3-1-dir は4回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _load_step2_from_dir(d: Path) -> str:
    p = d.resolve() / "02_response_step_2.txt"
    if not p.is_file():
        print(
            f"ERROR: {p} がありません（--step2-dir は3回目の gemini_step_tests/<UTC>/ を指定）",
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
        description="STANDARD-CP Gemini 13/15（手順7-2・タブ⑥2通目・チャット継続）"
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
        help="12回目テストの出力（01_prompt_step_7_1.txt・02_response_step_7_1.txt）",
    )
    parser.add_argument(
        "--step3-1-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="4回目フォルダ（02_response_step_3_1.txt）。--step3-1-response とは排他",
    )
    parser.add_argument(
        "--step2-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="3回目フォルダ（02_response_step_2.txt）。--step2-response とは排他",
    )
    parser.add_argument(
        "--step3-1-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順3-1 相当の応答テキスト。--step2-response とセットで指定",
    )
    parser.add_argument(
        "--step2-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順2 相当の応答テキスト。--step3-1-response とセットで指定",
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
    prev12 = args.prev_gemini_dir.resolve()
    p71, r71 = _load_step7_1_turn(prev12)

    has_dirs = args.step3_1_dir is not None and args.step2_dir is not None
    has_files = args.step3_1_response is not None and args.step2_response is not None
    partial_dir = (args.step3_1_dir is not None) ^ (args.step2_dir is not None)
    partial_file = (args.step3_1_response is not None) ^ (args.step2_response is not None)

    if partial_dir or partial_file:
        print(
            "ERROR: --step3-1-dir と --step2-dir は両方、または "
            "--step3-1-response と --step2-response は両方指定してください。",
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
            "ERROR: (--step3-1-dir と --step2-dir) または "
            "(--step3-1-response と --step2-response) が必要です。",
            file=sys.stderr,
        )
        sys.exit(1)

    if has_dirs:
        s31 = _load_step3_1_from_dir(args.step3_1_dir)
        s2 = _load_step2_from_dir(args.step2_dir)
        s31_ref = str(args.step3_1_dir.resolve())
        s2_ref = str(args.step2_dir.resolve())
    else:
        s31 = _load_text_file(args.step3_1_response, "--step3-1-response")
        s2 = _load_text_file(args.step2_response, "--step2-response")
        s31_ref = str(args.step3_1_response.resolve())
        s2_ref = str(args.step2_response.resolve())

    prompt, response = run_standard_cp_gemini_api_call_13_of_15(
        step_7_1_prompt=p71,
        step_7_1_response=r71,
        step_3_1_output=s31,
        step_2_output=s2,
    )

    base = pipeline_gemini_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_gemini_dir": str(prev12),
                "step3_1_source": s31_ref,
                "step2_source": s2_ref,
                "step31_via_files": not has_dirs,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_7_2.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_7_2.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_7_2",
        "gemini_call_index_1based": 13,
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
                "STANDARD-CP Gemini 段階テスト（手順7-2・API 13/15・タブ⑥2通目）",
                "",
                "00_source.json — phase1・run・12回目・3/4回目参照",
                "01_prompt_step_7_2.txt — step_7_2.txt 置換済み",
                "02_response_step_7_2.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は手順7-1で start_chat(history) を1往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 13/15（手順7-2・タブ⑥2通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
