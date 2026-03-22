#!/usr/bin/env python3
"""
フェーズ1スナップショット＋ **1回目の応答** を入力に、STANDARD-CP の Gemini **2/15（タブ②）**だけ実行する。
手順1-2 と 手順1-3 を **1メッセージに連結**して送信する（手作業マニュアルと同じ）。

1回目の成果物フォルダ（``02_response_step_1_1.txt`` があるディレクトリ）を ``--prev-gemini-dir`` で渡す::

  python3 scripts/gemini_standard_cp_step2_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-gemini-dir output/pipeline_test_runs/<run>/gemini_step_tests/<UTC>

応答テキストだけ別ファイルにある場合は ``--step1-response`` で指定::

  python3 scripts/gemini_standard_cp_step2_from_phase1.py \\
    --phase1-dir ... --step1-response path/to/02_response_step_1_1.txt

成果物は **同じ run 配下**の ``gemini_step_tests/<新UTC>/`` に保存（1回目と別フォルダ）。

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
from modules.standard_cp_gemini_manual import (  # noqa: E402
    run_standard_cp_gemini_api_call_2_of_15,
)


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


def _load_step1_response(prev_dir: Path | None, response_file: Path | None) -> str:
    if response_file is not None:
        p = response_file.resolve()
        if not p.is_file():
            print(f"ERROR: --step1-response が見つかりません: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8")
    if prev_dir is None:
        print(
            "ERROR: --prev-gemini-dir か --step1-response のどちらかが必要です。",
            file=sys.stderr,
        )
        sys.exit(1)
    d = prev_dir.resolve()
    inner = d / "02_response_step_1_1.txt"
    if not inner.is_file():
        print(
            f"ERROR: {inner} がありません（--prev-gemini-dir は1回目の gemini_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return inner.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Gemini 2/15（手順1-2+1-3 連結）をフェーズ1＋1回目応答で実行"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="phase1_snapshots/<UTC>/",
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--prev-gemini-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="1回目テストの出力ディレクトリ（02_response_step_1_1.txt を含む）",
    )
    g.add_argument(
        "--step1-response",
        type=Path,
        default=None,
        metavar="PATH",
        help="手順1-1 の応答テキストファイルへのパス",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="1 ラン用の親。省略時は phase1 から推定",
    )
    parser.add_argument(
        "--existing-site-url",
        type=str,
        default="",
        metavar="URL",
        help="既存サイト URL（本番の引数と同じ。省略時はヒアリングから推測のみ）",
    )
    args = parser.parse_args()

    phase1 = args.phase1_dir.resolve()
    run_root = _resolve_run_root(phase1=phase1, run_dir=args.run_dir)

    bundle = load_hearing_bundle_from_phase1_dir(phase1)
    step1_out = _load_step1_response(args.prev_gemini_dir, args.step1_response)

    prompt, response = run_standard_cp_gemini_api_call_2_of_15(
        hearing_sheet_content=bundle.hearing_sheet_content or "",
        appo_memo=bundle.appo_memo,
        sales_notes=bundle.sales_notes,
        existing_site_url=(args.existing_site_url or "").strip(),
        step_1_1_output=step1_out,
    )

    base = pipeline_gemini_step_tests_base(run_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    prev_ref: str | None = None
    if args.prev_gemini_dir is not None:
        prev_ref = str(args.prev_gemini_dir.resolve())
    step1_file: str | None = None
    if args.step1_response is not None:
        step1_file = str(args.step1_response.resolve())

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "phase1_dir": str(phase1),
                "run_root": str(run_root.resolve()),
                "prev_gemini_dir": prev_ref,
                "step1_response_file": step1_file,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_1_2_and_1_3.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_1_2_and_1_3.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_tab2_step_1_2_1_3_combined",
        "gemini_call_index_1based": 2,
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
                "STANDARD-CP Gemini 段階テスト（手順1-2+1-3 連結・API 2/15）",
                "",
                "00_source.json — phase1・run・1回目参照",
                "01_prompt_step_1_2_and_1_3.txt — 1-2 と 1-3 を連結したプロンプト",
                "02_response_step_1_2_and_1_3.txt — 応答（従来の手順1-3 相当の1本）",
                "meta.json — 文字数・メタ",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 2/15（手順1-2+1-3 連結・タブ②）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
