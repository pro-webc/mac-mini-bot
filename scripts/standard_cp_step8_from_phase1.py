#!/usr/bin/env python3
"""
**7回目の成果物**（手順3-4）と、その ``prev`` チェーン（6→5→4 回目）から **手順3-1〜3-3** を解決し、
STANDARD-CP の Claude **8/15（手順3-5・タブ④の5通目＝タブ④最終）**だけ実行する。

※ スクリプト名の ``step8`` は **段階テストの8回目（API 8/15）** を指し、本番の **手順8** とは無関係です。

7回目フォルダを ``--prev-step-dir`` で渡す（``01_prompt_step_3_4.txt`` / ``02_response_step_3_4.txt`` /
``00_source.json``）。``prev_step_dir`` を最大3回辿り 6→5→4 回目から 3-3・3-2・3-1 を読む。

::

  python3 scripts/standard_cp_step8_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<7回目UTC>

チェーン欠け時は ``--step3-3-*`` / ``--step3-2-*`` / ``--step3-1-*`` を **各ペアで** 指定。

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_8_of_15  # noqa: E402


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


def _read_prompt_response(d: Path, prompt_name: str, resp_name: str) -> tuple[str, str]:
    pp = d / prompt_name
    pr = d / resp_name
    if not pp.is_file():
        print(f"ERROR: {pp} がありません。", file=sys.stderr)
        sys.exit(1)
    if not pr.is_file():
        print(f"ERROR: {pr} がありません。", file=sys.stderr)
        sys.exit(1)
    return pp.read_text(encoding="utf-8"), pr.read_text(encoding="utf-8")


def _load_prev_dir_from_source(folder: Path, label: str) -> Path:
    meta = folder / "00_source.json"
    if not meta.is_file():
        print(f"ERROR: {meta} がありません（{label}）。", file=sys.stderr)
        sys.exit(1)
    data = json.loads(meta.read_text(encoding="utf-8"))
    pgm = data.get("prev_step_dir")
    if not pgm:
        print(
            f"ERROR: {label} の 00_source.json に prev_step_dir がありません。",
            file=sys.stderr,
        )
        sys.exit(1)
    return Path(str(pgm))


def _optional_pair(
    prompt_path: Path | None,
    response_path: Path | None,
    flag_label: str,
) -> tuple[str, str] | None:
    if prompt_path is None and response_path is None:
        return None
    if prompt_path is None or response_path is None:
        print(
            f"ERROR: {flag_label} はプロンプトと応答を両方指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    pp = prompt_path.resolve()
    pr = response_path.resolve()
    if not pp.is_file():
        print(f"ERROR: プロンプトが見つかりません: {pp}", file=sys.stderr)
        sys.exit(1)
    if not pr.is_file():
        print(f"ERROR: 応答が見つかりません: {pr}", file=sys.stderr)
        sys.exit(1)
    return pp.read_text(encoding="utf-8"), pr.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "STANDARD-CP Claude 8/15（手順3-5・タブ④5通目）。"
            "段階テスト8回目。"
        )
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
        help="7回目テストの出力（3-4 の prompt/response・00_source.json）",
    )
    parser.add_argument(
        "--step3-3-prompt",
        type=Path,
        default=None,
        metavar="PATH",
        help="6回目の 01_prompt_step_3_3.txt の上書き（--step3-3-response と併用）",
    )
    parser.add_argument(
        "--step3-3-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="6回目の 02_response_step_3_3.txt の上書き（--step3-3-prompt と併用）",
    )
    parser.add_argument(
        "--step3-2-prompt",
        type=Path,
        default=None,
        metavar="PATH",
        help="5回目の 01_prompt_step_3_2.txt の上書き（--step3-2-response と併用）",
    )
    parser.add_argument(
        "--step3-2-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="5回目の 02_response_step_3_2.txt の上書き（--step3-2-prompt と併用）",
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
    prev7 = args.prev_step_dir.resolve()

    p34, r34 = _read_prompt_response(
        prev7,
        "01_prompt_step_3_4.txt",
        "02_response_step_3_4.txt",
    )

    dir6 = _load_prev_dir_from_source(prev7, "7回目")
    o33 = _optional_pair(
        args.step3_3_prompt,
        args.step3_3_response,
        "--step3-3-prompt / --step3-3-response",
    )
    if o33 is not None:
        p33, r33 = o33
    else:
        p33, r33 = _read_prompt_response(
            dir6,
            "01_prompt_step_3_3.txt",
            "02_response_step_3_3.txt",
        )

    dir5 = _load_prev_dir_from_source(dir6, "6回目")
    o32 = _optional_pair(
        args.step3_2_prompt,
        args.step3_2_response,
        "--step3-2-prompt / --step3-2-response",
    )
    if o32 is not None:
        p32, r32 = o32
    else:
        p32, r32 = _read_prompt_response(
            dir5,
            "01_prompt_step_3_2.txt",
            "02_response_step_3_2.txt",
        )

    dir4 = _load_prev_dir_from_source(dir5, "5回目")
    o31 = _optional_pair(
        args.step3_1_prompt,
        args.step3_1_response,
        "--step3-1-prompt / --step3-1-response",
    )
    if o31 is not None:
        p31, r31 = o31
    else:
        p31, r31 = _read_prompt_response(
            dir4,
            "01_prompt_step_3_1.txt",
            "02_response_step_3_1.txt",
        )

    prompt, response = run_standard_cp_claude_api_call_8_of_15(
        step_3_1_prompt=p31,
        step_3_1_response=r31,
        step_3_2_prompt=p32,
        step_3_2_response=r32,
        step_3_3_prompt=p33,
        step_3_3_response=r33,
        step_3_4_prompt=p34,
        step_3_4_response=r34,
    )

    base = pipeline_claude_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    overrides: dict[str, str | None] = {
        "step3_3": None,
        "step3_2": None,
        "step3_1": None,
    }
    if args.step3_3_prompt is not None:
        overrides["step3_3"] = str(args.step3_3_prompt.resolve())
    if args.step3_2_prompt is not None:
        overrides["step3_2"] = str(args.step3_2_prompt.resolve())
    if args.step3_1_prompt is not None:
        overrides["step3_1"] = str(args.step3_1_prompt.resolve())

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_step_dir": str(prev7),
                "prompt_overrides": overrides,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_3_5.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_3_5.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_3_5",
        "claude_call_index_1based": 8,
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
                "STANDARD-CP Claude 段階テスト（手順3-5・API 8/15・タブ④5通目・タブ④終了）",
                "",
                "00_source.json — phase1・run・7回目参照",
                "01_prompt_step_3_5.txt — step_3_5.txt 本文（置換なし）",
                "02_response_step_3_5.txt — 応答（残りページ案など）",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は 3-1〜3-4 のプロンプト/応答で start_chat(history) を4往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 8/15（手順3-5・タブ④5通目・段階テスト8回目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
