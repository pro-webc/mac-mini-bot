#!/usr/bin/env python3
"""
**5回目の成果物**（手順3-2）と **4回目**（手順3-1）を入力に、STANDARD-CP の Claude **6/15（手順3-3・タブ④の3通目）**だけ実行する。

5回目フォルダ（``01_prompt_step_3_2.txt`` / ``02_response_step_3_2.txt`` / ``00_source.json``）を ``--prev-step-dir`` で渡す。
``00_source.json`` の ``prev_step_dir`` から4回目を辿り、手順3-1 のプロンプト/応答を読む。

::

  python3 scripts/standard_cp_step6_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<5回目UTC>

4回目が別マシンにあるなどで辿れない場合は ``--step3-1-prompt`` / ``--step3-1-response`` で明示する。

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_6_of_15  # noqa: E402


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


def _load_step3_2_turn(prev_dir: Path) -> tuple[str, str]:
    d = prev_dir.resolve()
    p_p = d / "01_prompt_step_3_2.txt"
    p_r = d / "02_response_step_3_2.txt"
    if not p_p.is_file():
        print(
            f"ERROR: {p_p} がありません（--prev-step-dir は5回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_r.is_file():
        print(
            f"ERROR: {p_r} がありません（--prev-step-dir は5回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_p.read_text(encoding="utf-8"), p_r.read_text(encoding="utf-8")


def _load_step3_1_turn(
    prev_fifth: Path,
    prompt_override: Path | None,
    response_override: Path | None,
) -> tuple[str, str]:
    if prompt_override is not None and response_override is not None:
        pp = prompt_override.resolve()
        pr = response_override.resolve()
        if not pp.is_file():
            print(f"ERROR: --step3-1-prompt が見つかりません: {pp}", file=sys.stderr)
            sys.exit(1)
        if not pr.is_file():
            print(f"ERROR: --step3-1-response が見つかりません: {pr}", file=sys.stderr)
            sys.exit(1)
        return pp.read_text(encoding="utf-8"), pr.read_text(encoding="utf-8")
    if prompt_override is not None or response_override is not None:
        print(
            "ERROR: --step3-1-prompt と --step3-1-response は両方指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    meta_path = prev_fifth.resolve() / "00_source.json"
    if not meta_path.is_file():
        print(
            f"ERROR: {meta_path} がありません。--step3-1-prompt / --step3-1-response で指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    pgm = data.get("prev_step_dir")
    if not pgm:
        print(
            "ERROR: 00_source.json に prev_step_dir がありません。"
            "--step3-1-prompt / --step3-1-response を指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    fourth = Path(str(pgm))
    p_p = fourth / "01_prompt_step_3_1.txt"
    p_r = fourth / "02_response_step_3_1.txt"
    if not p_p.is_file() or not p_r.is_file():
        print(
            f"ERROR: 手順3-1 のファイルが見つかりません: {p_p} / {p_r}",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_p.read_text(encoding="utf-8"), p_r.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 6/15（手順3-3・タブ④3通目・チャット継続）"
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
        help="5回目テストの出力（3-2 の prompt/response・00_source.json を含む）",
    )
    parser.add_argument(
        "--step3-1-prompt",
        type=Path,
        default=None,
        metavar="PATH",
        help="4回目の 01_prompt_step_3_1.txt の上書き（--step3-1-response と併用）",
    )
    parser.add_argument(
        "--step3-1-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="4回目の 02_response_step_3_1.txt の上書き（--step3-1-prompt と併用）",
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

    p32, r32 = _load_step3_2_turn(prev)
    p31, r31 = _load_step3_1_turn(
        prev,
        args.step3_1_prompt,
        args.step3_1_response,
    )

    prompt, response = run_standard_cp_claude_api_call_6_of_15(
        step_3_1_prompt=p31,
        step_3_1_response=r31,
        step_3_2_prompt=p32,
        step_3_2_response=r32,
    )

    base = pipeline_claude_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    s31_override = None
    if args.step3_1_prompt is not None:
        s31_override = {
            "prompt": str(args.step3_1_prompt.resolve()),
            "response": str(args.step3_1_response.resolve()),
        }

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_step_dir": str(prev),
                "step3_1_override": s31_override,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_3_3.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_3_3.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_3_3",
        "claude_call_index_1based": 6,
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
                "STANDARD-CP Claude 段階テスト（手順3-3・API 6/15・タブ④3通目）",
                "",
                "00_source.json — phase1・run・5回目参照",
                "01_prompt_step_3_3.txt — step_3_3.txt 本文（置換なし）",
                "02_response_step_3_3.txt — 応答（会社概要ページ案など）",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は 3-1・3-2 のプロンプト/応答で start_chat(history) を2往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 6/15（手順3-3・タブ④3通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
