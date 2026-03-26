#!/usr/bin/env python3
"""
**3回目の応答**（手順2・6ページ構成など）を入力に、STANDARD-CP の Claude **4/15（手順3-1・タブ④の1通目）**だけ実行する。

3回目の成果物フォルダ（``02_response_step_2.txt`` と ``00_source.json`` があるディレクトリ）を ``--prev-step-dir`` で渡す。
手順1-3 相当の本文は、``00_source.json`` の ``prev_step_dir`` 配下の
``02_response_step_1_2_and_1_3.txt``、または ``step1_3_response_file`` から自動解決する。

::

  python3 scripts/standard_cp_step4_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<3回目UTC>

上記の自動解決が使えない場合は ``--step1-3-response`` で手順1-3の応答ファイルを明示する。
``--step2-response`` で手順2の応答ファイルを上書きできる。

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_4_of_15  # noqa: E402


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


def _load_step2_response(prev_dir: Path, step2_file: Path | None) -> str:
    if step2_file is not None:
        p = step2_file.resolve()
        if not p.is_file():
            print(f"ERROR: --step2-response が見つかりません: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8")
    inner = prev_dir.resolve() / "02_response_step_2.txt"
    if not inner.is_file():
        print(
            f"ERROR: {inner} がありません（--prev-step-dir は3回目の claude_step_tests/<UTC>/ を指定、"
            "または --step2-response で明示）",
            file=sys.stderr,
        )
        sys.exit(1)
    return inner.read_text(encoding="utf-8")


def _load_step1_3_for_step4(
    prev_dir: Path,
    step1_3_override: Path | None,
) -> str:
    if step1_3_override is not None:
        p = step1_3_override.resolve()
        if not p.is_file():
            print(f"ERROR: --step1-3-response が見つかりません: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8")

    meta_path = prev_dir.resolve() / "00_source.json"
    if not meta_path.is_file():
        print(
            f"ERROR: {meta_path} がありません。--step1-3-response で手順1-3応答を指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    alt = data.get("step1_3_response_file")
    if alt:
        p = Path(str(alt))
        if not p.is_file():
            print(
                f"ERROR: 00_source.json の step1_3_response_file が無効です: {p}",
                file=sys.stderr,
            )
            sys.exit(1)
        return p.read_text(encoding="utf-8")
    pgm = data.get("prev_step_dir")
    if not pgm:
        print(
            "ERROR: 00_source.json に prev_step_dir がありません。"
            "--step1-3-response で 02_response_step_1_2_and_1_3.txt 相当を指定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    inner = Path(str(pgm)) / "02_response_step_1_2_and_1_3.txt"
    if not inner.is_file():
        print(
            f"ERROR: 手順1-3応答が見つかりません: {inner}",
            file=sys.stderr,
        )
        sys.exit(1)
    return inner.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 4/15（手順3-1・タブ④1通目）を手順2+手順1-3で実行"
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
        help="3回目テストの出力（02_response_step_2.txt・00_source.json を含む）",
    )
    parser.add_argument(
        "--step2-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順2応答の上書き（省略時は prev 内の 02_response_step_2.txt）",
    )
    parser.add_argument(
        "--step1-3-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順1-3応答の明示（省略時は 00_source.json から2回目フォルダを辿る）",
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

    step2_text = _load_step2_response(prev, args.step2_response)
    step13_text = _load_step1_3_for_step4(prev, args.step1_3_response)
    step2_path_used = (
        args.step2_response.resolve()
        if args.step2_response is not None
        else (prev / "02_response_step_2.txt").resolve()
    )

    prompt, response = run_standard_cp_claude_api_call_4_of_15(
        step_2_output=step2_text,
        step_1_3_output=step13_text,
    )

    base = pipeline_claude_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    step13_src: str | None = None
    if args.step1_3_response is not None:
        step13_src = str(args.step1_3_response.resolve())

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_step_dir": str(prev),
                "step2_response_file": str(step2_path_used),
                "step1_3_response_file": step13_src,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_3_1.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_3_1.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_3_1",
        "claude_call_index_1based": 4,
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
                "STANDARD-CP Claude 段階テスト（手順3-1・API 4/15・タブ④1通目）",
                "",
                "00_source.json — phase1・run・3回目参照",
                "01_prompt_step_3_1.txt — step_3_1.txt 置換済みプロンプト",
                "02_response_step_3_1.txt — 応答（TOPページ案など）",
                "meta.json — 文字数・メタ",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 4/15（手順3-1・タブ④1通目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
