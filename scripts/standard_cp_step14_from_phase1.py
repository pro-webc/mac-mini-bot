#!/usr/bin/env python3
"""
**12回目**（手順7-1）と **13回目**（手順7-2）のプロンプト＋応答でタブ⑥を2往復復元し、
**5〜6回目**（手順3-2〜3-3）の応答を束ねて ``STEP_3_LOWER_BATCH1`` とし、
STANDARD-CP の Claude **14/16（手順7-3・タブ⑥の3通目・下層1群目）**だけ実行する。

12回目・13回目の解決:
  ``--prev-step-dir`` は **13回目**フォルダ（``01_prompt_step_7_2.txt`` 等）。
  ``00_source.json`` の ``prev_step_dir`` から **12回目**を辿り手順7-1を復元する。

下層ページ本文:
  ``--step32-dir`` … **5回目**（``02_response_step_3_2.txt``）
  ``--step33-dir`` … **6回目**（``02_response_step_3_3.txt``）
  ``--step34-dir`` … **7回目**（``02_response_step_3_4.txt``）
  ``--step35-dir`` … **8回目**（``02_response_step_3_5.txt``）

まとめテキストを直接渡す場合は ``--subpages-output-file PATH``（上記4ディレクトリと排他）。

::

  python3 scripts/standard_cp_step14_from_phase1.py \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC> \\
    --prev-step-dir output/pipeline_test_runs/<run>/claude_step_tests/<13回目UTC> \\
    --step32-dir .../claude_step_tests/<5回目UTC> \\
    --step33-dir .../claude_step_tests/<6回目UTC> \\
    --step34-dir .../claude_step_tests/<7回目UTC> \\
    --step35-dir .../claude_step_tests/<8回目UTC>

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
from modules.standard_cp_claude_manual import run_standard_cp_claude_api_call_14_of_16  # noqa: E402


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


def _load_step7_1_from_prev12(prev12: Path) -> tuple[str, str]:
    d = prev12.resolve()
    p_p = d / "01_prompt_step_7_1.txt"
    p_r = d / "02_response_step_7_1.txt"
    if not p_p.is_file() or not p_r.is_file():
        print(
            f"ERROR: {d} に手順7-1の保存がありません（12回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_p.read_text(encoding="utf-8"), p_r.read_text(encoding="utf-8")


def _load_step7_2_turn(prev13: Path) -> tuple[str, str]:
    d = prev13.resolve()
    p_p = d / "01_prompt_step_7_2.txt"
    p_r = d / "02_response_step_7_2.txt"
    if not p_p.is_file():
        print(
            f"ERROR: {p_p} がありません（--prev-step-dir は13回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    if not p_r.is_file():
        print(
            f"ERROR: {p_r} がありません（--prev-step-dir は13回目の claude_step_tests/<UTC>/ を指定）",
            file=sys.stderr,
        )
        sys.exit(1)
    return p_p.read_text(encoding="utf-8"), p_r.read_text(encoding="utf-8")


def _resolve_step7_1_from_chain(prev13: Path) -> tuple[str, str]:
    src_path = prev13.resolve() / "00_source.json"
    if not src_path.is_file():
        print(
            f"ERROR: {src_path} がありません。13回目の出力フォルダを指定するか、"
            " --step7-1-dir で12回目フォルダを明示してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(src_path.read_text(encoding="utf-8"))
    prev12 = data.get("prev_step_dir")
    if not prev12:
        print("ERROR: 00_source.json に prev_step_dir がありません。", file=sys.stderr)
        sys.exit(1)
    return _load_step7_1_from_prev12(Path(prev12))


def _read_response(d: Path, filename: str, label: str) -> str:
    p = d.resolve() / filename
    if not p.is_file():
        print(f"ERROR: {label}: {p} がありません。", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _build_batch1_from_dirs(
    d32: Path,
    d33: Path,
) -> str:
    s2 = _read_response(d32, "02_response_step_3_2.txt", "--step32-dir")
    s3 = _read_response(d33, "02_response_step_3_3.txt", "--step33-dir")
    return (
        "\n\n=== 手順3-2 サービスページ ===\n\n"
        + s2
        + "\n\n=== 手順3-3 会社概要 ===\n\n"
        + s3
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STANDARD-CP Claude 14/16（手順7-3・タブ⑥3通目・下層1群目）"
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
        help="13回目テストの出力（手順7-2）。00_source.json で12回目を辿る",
    )
    parser.add_argument(
        "--step7-1-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="12回目フォルダを明示（省略時は 13回目/00_source.json の prev_step_dir）",
    )
    parser.add_argument(
        "--step32-dir",
        type=Path,
        default=None,
        metavar="DIR",
    )
    parser.add_argument(
        "--step33-dir",
        type=Path,
        default=None,
        metavar="DIR",
    )
    parser.add_argument(
        "--batch1-output-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="STEP_3_LOWER_BATCH1 相当の全文テキスト（2ディレクトリ指定と排他）",
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
    prev13 = args.prev_step_dir.resolve()
    p72, r72 = _load_step7_2_turn(prev13)

    if args.step7_1_dir is not None:
        p71, r71 = _load_step7_1_from_prev12(args.step7_1_dir)
        step12_ref = str(args.step7_1_dir.resolve())
    else:
        p71, r71 = _resolve_step7_1_from_chain(prev13)
        step12_ref = str(
            Path(
                json.loads(
                    (prev13 / "00_source.json").read_text(encoding="utf-8")
                )["prev_step_dir"]
            ).resolve()
        )

    has_dirs = all(
        x is not None for x in (args.step32_dir, args.step33_dir)
    )
    has_partial_dirs = any(
        x is not None for x in (args.step32_dir, args.step33_dir)
    ) and not has_dirs
    has_file = args.batch1_output_file is not None

    if has_partial_dirs:
        print(
            "ERROR: --step32-dir / --step33-dir は"
            " 両方指定するか、省略して --batch1-output-file を使ってください。",
            file=sys.stderr,
        )
        sys.exit(1)
    if has_dirs and has_file:
        print(
            "ERROR: ディレクトリ指定と --batch1-output-file は同時に使えません。",
            file=sys.stderr,
        )
        sys.exit(1)
    if not has_dirs and not has_file:
        print(
            "ERROR: (--step32-dir + --step33-dir) または "
            "--batch1-output-file が必要です。",
            file=sys.stderr,
        )
        sys.exit(1)

    if has_file:
        p = args.batch1_output_file.resolve()
        if not p.is_file():
            print(f"ERROR: --batch1-output-file が見つかりません: {p}", file=sys.stderr)
            sys.exit(1)
        batch1 = p.read_text(encoding="utf-8")
        sub_ref = str(p)
        via_file = True
    else:
        batch1 = _build_batch1_from_dirs(
            args.step32_dir,
            args.step33_dir,
        )
        sub_ref = {
            "step32": str(args.step32_dir.resolve()),
            "step33": str(args.step33_dir.resolve()),
        }
        via_file = False

    prompt, response = run_standard_cp_claude_api_call_14_of_16(
        step_7_1_prompt=p71,
        step_7_1_response=r71,
        step_7_2_prompt=p72,
        step_7_2_response=r72,
        step_3_lower_batch1=batch1,
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
                "prev_step_dir": str(prev13),
                "step7_1_dir": step12_ref,
                "batch1_source": sub_ref,
                "batch1_via_file": via_file,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "01_prompt_step_7_3.txt").write_text(prompt, encoding="utf-8")
    (out / "02_response_step_7_3.txt").write_text(response, encoding="utf-8")
    meta = {
        "run_root": str(run_root.resolve()),
        "phase1_dir": str(phase1),
        "step": "standard_cp_manual_step_7_3",
        "claude_call_index_1based": 14,
        "claude_calls_total_standard_cp": 16,
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
                "STANDARD-CP Claude 段階テスト（手順7-3・API 14/16・タブ⑥3通目・下層1群目）",
                "",
                "00_source.json — phase1・run・13回目・12回目・下層1群目参照",
                "01_prompt_step_7_3.txt — step_7_3.txt 置換済み",
                "02_response_step_7_3.txt — 応答",
                "meta.json — 文字数・メタ",
                "",
                "※ API 呼び出し時は手順7-1・7-2で start_chat(history) を2往復復元済み。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("--- 14/16（手順7-3・タブ⑥3通目・下層1群目）---")
    print(f"run_root: {run_root.resolve()}")
    print(f"phase1_dir: {phase1}")
    print(f"保存: {out}")
    print(f"プロンプト: {len(prompt)} 文字 / 応答: {len(response)} 文字")


if __name__ == "__main__":
    main()
