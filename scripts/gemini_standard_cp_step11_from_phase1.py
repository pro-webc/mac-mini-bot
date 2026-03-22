#!/usr/bin/env python3
"""
**10回目の成果物**（手順5 のプロンプト＋応答）と ``00_source.json`` の ``prev_gemini_dir``（9回目・手順4）で
タブ⑤チャットを2往復復元し、STANDARD-CP の Gemini **11/15（手順6・タブ⑤の3通目）**だけ実行する。

::

  python3 scripts/gemini_standard_cp_step11_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-gemini-dir output/pipeline_test_runs/<run>/gemini_step_tests/<10回目UTC>

9回目フォルダを直接渡す場合（``00_source.json`` が無いとき）は ``--step4-dir`` を追加。

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
from modules.standard_cp_gemini_manual import run_standard_cp_gemini_api_call_11_of_15  # noqa: E402


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
            f"ERROR: {p_prompt} がありません（--step4-dir は9回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_resp.is_file():
        print(
            f"ERROR: {p_resp} がありません（--step4-dir は9回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_prompt.read_text(encoding="utf-8"), p_resp.read_text(encoding="utf-8")


def _load_step10_turn(prev10: Path) -> tuple[str, str, str, str]:
    """10回目フォルダから (p4,r4,p5,r5) を返す。"""
    d = prev10.resolve()
    p5p = d / "01_prompt_step_5.txt"
    p5r = d / "02_response_step_5.txt"
    if not p5p.is_file():
        print(
            f"ERROR: {p5p} がありません（--prev-gemini-dir は10回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p5r.is_file():
        print(
            f"ERROR: {p5r} がありません（--prev-gemini-dir は10回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    src_path = d / "00_source.json"
    if not src_path.is_file():
        print(
            f"ERROR: {src_path} がありません。10回目の出力フォルダを指定するか、"
            " --step4-dir で9回目（手順4）フォルダを明示してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    src = json.loads(src_path.read_text(encoding="utf-8"))
    prev9 = src.get("prev_gemini_dir")
    if not prev9:
        print("ERROR: 00_source.json に prev_gemini_dir がありません。", file=sys.stderr)
        sys.exit(1)
    p4, r4 = _load_step4_turn(Path(prev9))
    return p4, r4, p5p.read_text(encoding="utf-8"), p5r.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Gemini 11/15（手順6・タブ⑤3通目・チャット継続）"
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
        help="10回目テストの出力（01_prompt_step_5.txt・02_response_step_5.txt・00_source.json）",
    )
    parser.add_argument(
        "--step4-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="省略時は 00_source.json の prev_gemini_dir。無い場合に9回目フォルダを明示",
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
    prev10 = args.prev_gemini_dir.resolve()

    p5 = prev10 / "01_prompt_step_5.txt"
    r5 = prev10 / "02_response_step_5.txt"
    if not p5.is_file() or not r5.is_file():
        print(
            "ERROR: --prev-gemini-dir に 01_prompt_step_5.txt / 02_response_step_5.txt が必要です。",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.step4_dir is not None:
        p4, r4 = _load_step4_turn(args.step4_dir)
        p5_text = p5.read_text(encoding="utf-8")
        r5_text = r5.read_text(encoding="utf-8")
        step4_ref = str(args.step4_dir.resolve())
    else:
        p4, r4, p5_text, r5_text = _load_step10_turn(prev10)
        src = json.loads((prev10 / "00_source.json").read_text(encoding="utf-8"))
        step4_ref = str(Path(src["prev_gemini_dir"]).resolve())

    prompt, response = run_standard_cp_gemini_api_call_11_of_15(
        step_4_prompt=p4,
        step_4_response=r4,
        step_5_prompt=p5_text,
        step_5_response=r5_text,
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
                "prev_gemini_dir": str(prev10),
                "step4_dir": step4_ref,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_6.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_6.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_6",
        "gemini_call_index_1based": 11,
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
                "STANDARD-CP Gemini 段階テスト（手順6・API 11/15・タブ⑤3通目）",
                "",
                "00_source.json — phase1・run・10回目・手順4フォルダ参照",
                "01_prompt_step_6.txt — step_6.txt 本文",
                "02_response_step_6.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は手順4・5で start_chat(history) を2往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 11/15（手順6・タブ⑤3通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
