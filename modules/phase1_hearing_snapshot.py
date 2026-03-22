"""プリフライト等の ``04_pending_cases.json`` からフェーズ1（ヒアリング抽出）だけ実行し保存する。"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import (
    OUTPUT_DIR,
    latest_preflight_cases_path,
    pipeline_phase1_snapshots_base,
)
from config.logging_setup import configure_logging

configure_logging()

from modules.case_extraction import extract_hearing_bundle
from modules.spec_generator import SpecGenerator


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_utf8_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def snapshot_phase1_from_cases_json(
    cases_json_path: Path,
    *,
    case_index: int = 0,
    output_root: Path | None = None,
) -> Path:
    """
    ``04_pending_cases.json``（案件 dict のリスト）から 1 件選び、
    本番 ``process_case`` と同じ ``extract_hearing_bundle`` を実行して結果を保存する。

    Args:
        cases_json_path: プリフライトの ``04_pending_cases.json`` など
        case_index: リストの何件目を使うか（既定: 先頭）
        output_root: 未指定時は ``pipeline_phase1_snapshots_base()``（``PIPELINE_TEST_RUN_DIR`` 対応）

    Returns:
        保存先ディレクトリ
    """
    p = cases_json_path.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"cases JSON が見つかりません: {p}")

    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"JSON は非空のリストである必要があります: {p}")
    if case_index < 0 or case_index >= len(raw):
        raise IndexError(
            f"case_index={case_index} が範囲外です（0..{len(raw) - 1}）"
        )

    case: dict[str, Any] = raw[case_index]
    base = output_root or (OUTPUT_DIR / "phase1_snapshots")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    _write_json(
        out / "00_source.json",
        {
            "cases_json": str(p),
            "case_index": case_index,
            "cases_total": len(raw),
        },
    )

    meta = {
        "row_number": case.get("row_number"),
        "record_number": case.get("record_number"),
        "partner_name": case.get("partner_name"),
        "contract_plan": case.get("contract_plan"),
    }
    _write_json(out / "01_case_meta.json", meta)

    spec_gen = SpecGenerator()
    bundle = extract_hearing_bundle(
        case,
        fetch_hearing_sheet=spec_gen.fetch_hearing_sheet,
    )

    h_raw = bundle.hearing_sheet_content or ""
    a_raw = bundle.appo_memo or ""
    s_raw = bundle.sales_notes or ""
    hearing = h_raw.strip()

    # 手作業・コピペ用（本文は .txt。巨大 JSON 1 ファイルを避ける）
    _write_utf8_text(out / "hearing_sheet_content.txt", h_raw)
    _write_utf8_text(out / "appo_memo.txt", a_raw)
    _write_utf8_text(out / "sales_notes.txt", s_raw)

    _write_json(
        out / "02_hearing_bundle_summary.json",
        {
            "hearing_sheet_content_chars": len(h_raw),
            "appo_memo_chars": len(a_raw),
            "sales_notes_chars": len(s_raw),
            "hearing_non_empty": bool(hearing),
            "would_skip_in_main": not hearing,
            "text_files": [
                "hearing_sheet_content.txt",
                "appo_memo.txt",
                "sales_notes.txt",
            ],
        },
    )

    (out / "README.txt").write_text(
        "\n".join(
            [
                "フェーズ1スナップショット（extract_hearing_bundle）",
                "",
                "00_source.json — 入力 JSON のパスと case_index",
                "01_case_meta.json — row / record / partner / plan（要約）",
                "hearing_sheet_content.txt — ヒアリング本文（LLM 原料・コピペ用）",
                "appo_memo.txt — アポ録音メモ",
                "sales_notes.txt — 営業メモ",
                "02_hearing_bundle_summary.json — 各 .txt の文字数・main でスキップするか",
                "",
                "main.process_case では hearing_sheet_content が空のとき AV を更新して return None します。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def main_argv(argv: list[str] | None = None) -> None:
    """CLI 用（scripts から呼ぶ）。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="04_pending_cases.json からフェーズ1を実行し phase1_snapshots に保存"
    )
    parser.add_argument(
        "cases_json",
        nargs="?",
        default=None,
        help="04_pending_cases.json のパス（省略時は最新の preflight_snapshots を探す）",
    )
    parser.add_argument(
        "--case-index",
        type=int,
        default=0,
        help="リストの何件目か（既定: 0）",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "1 ラン用の親ディレクトリ（その下に preflight_snapshots / phase1_snapshots を使う）。"
            " 省略時は PIPELINE_TEST_RUN_DIR または output/"
        ),
    )
    args = parser.parse_args(argv)

    rr = args.run_dir.resolve() if args.run_dir else None

    path: Path | None
    if args.cases_json:
        path = Path(args.cases_json)
    else:
        path = latest_preflight_cases_path(run_root=rr)
        if path is None:
            print(
                "ERROR: cases_json 未指定かつ preflight_snapshots/*/04_pending_cases.json がありません",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"入力（自動選択）: {path}")

    out = snapshot_phase1_from_cases_json(
        path,
        case_index=args.case_index,
        output_root=pipeline_phase1_snapshots_base(rr),
    )
    print(f"保存先: {out}")


if __name__ == "__main__":
    main_argv()
