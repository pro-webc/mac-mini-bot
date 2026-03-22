#!/usr/bin/env python3
"""
工程テスト **Manus のみ**（GitHub push / Vercel は行わない）。

Gemini 工程テストの **最終応答**を Canvas として読み、本番と同じ ``run_basic_lp_refactor_stage`` を 1 回実行する。
STANDARD-CP の最終は多くの場合 ``02_response_step_7_4.txt``（15/15 フォルダ内）。

成果物（既定: 同じ run 配下 ``manus_only_tests/<UTC>/``）::

  01_refactored_markdown.md   — Manus 返答本文（BOT_DEPLOY 行は除去済みの場合あり）
  02_summary.json             — メタ・文字数・取得した Git URL（あれば）
  03_deploy_github_url.txt    — 次工程 ``pipeline_test_deploy_only.py`` 用（1 行 URL または空）

例::

  python3 scripts/pipeline_test_manus_only.py \\
    --gemini-dir output/pipeline_test_runs/<run>/gemini_step_tests/<15回目UTC>/ \\
    --phase1-dir output/pipeline_test_runs/<run>/phase1_snapshots/<UTC>/

リポジトリルートで実行。.env に ``MANUS_API_KEY`` 必須。
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
    OUTPUT_DIR,
    pipeline_run_root_from_phase1_snapshot_dir,
)
from config.logging_setup import configure_logging  # noqa: E402


def _resolve_canvas_path(gemini_dir: Path | None, canvas_file: Path | None) -> Path:
    if canvas_file is not None:
        p = canvas_file.resolve()
        if not p.is_file():
            raise FileNotFoundError(f"--canvas-file が見つかりません: {p}")
        return p
    if gemini_dir is None:
        raise ValueError("--canvas-file か --gemini-dir のどちらかが必要です")
    d = gemini_dir.resolve()
    for name in (
        "02_response_step_7_4.txt",
        "02_response_step_8_3.txt",
    ):
        cand = d / name
        if cand.is_file():
            return cand
    raise FileNotFoundError(
        f"{d} に 02_response_step_7_4.txt または 02_response_step_8_3.txt がありません"
    )


def _resolve_out_dir(
    *,
    explicit: Path | None,
    phase1_dir: Path | None,
    gemini_dir: Path | None,
) -> Path:
    if explicit is not None:
        return explicit.resolve()
    if phase1_dir is not None:
        rr = pipeline_run_root_from_phase1_snapshot_dir(phase1_dir)
        if rr is not None:
            base = rr / "manus_only_tests"
        else:
            base = OUTPUT_DIR.resolve() / "pipeline_test_runs" / "manus_only_tests"
    elif gemini_dir is not None:
        src = gemini_dir.resolve() / "00_source.json"
        if src.is_file():
            data = json.loads(src.read_text(encoding="utf-8"))
            rr = data.get("run_root")
            if rr:
                base = Path(rr) / "manus_only_tests"
            else:
                base = gemini_dir.resolve().parent.parent / "manus_only_tests"
        else:
            base = gemini_dir.resolve().parent.parent / "manus_only_tests"
    else:
        base = OUTPUT_DIR.resolve() / "pipeline_test_runs" / "manus_only_tests"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return base / stamp


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="工程テスト: Manus のみ")
    parser.add_argument("--canvas-file", type=Path, default=None, metavar="PATH")
    parser.add_argument("--gemini-dir", type=Path, default=None, metavar="DIR")
    parser.add_argument("--phase1-dir", type=Path, default=None, metavar="DIR")
    parser.add_argument("--partner-name", type=str, default=None)
    parser.add_argument("--record-number", type=str, default=None)
    parser.add_argument("--out-dir", type=Path, default=None, metavar="DIR")
    args = parser.parse_args()

    canvas_path = _resolve_canvas_path(args.gemini_dir, args.canvas_file)
    canvas = canvas_path.read_text(encoding="utf-8")

    partner = args.partner_name
    record = args.record_number
    if args.phase1_dir is not None:
        from modules.phase2_text_llm_snapshot import load_phase1_case_meta

        meta = load_phase1_case_meta(args.phase1_dir)
        partner = partner or str(meta.get("partner_name") or "").strip() or None
        record = record or str(meta.get("record_number") or "").strip() or None
    if not partner:
        partner = "工程テスト"
    if record is None or record == "":
        record = "0"

    out = _resolve_out_dir(
        explicit=args.out_dir,
        phase1_dir=args.phase1_dir,
        gemini_dir=args.gemini_dir,
    )
    out.mkdir(parents=True, exist_ok=True)

    (out / "00_source.json").write_text(
        json.dumps(
            {
                "canvas_file": str(canvas_path),
                "partner_name": partner,
                "record_number": record,
                "phase1_dir": str(args.phase1_dir) if args.phase1_dir else None,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    from modules.basic_lp_refactor_gemini import run_basic_lp_refactor_stage

    print(f"Canvas: {canvas_path} ({len(canvas)} chars)")
    print(f"partner={partner!r} record={record!r}")
    print("Manus タスク実行中（完了までポーリング）…")

    md, gh_url = run_basic_lp_refactor_stage(
        canvas_source_code=canvas,
        partner_name=partner,
        record_number=record,
    )

    (out / "01_refactored_markdown.md").write_text(md, encoding="utf-8")
    url_str = (gh_url or "").strip()
    (out / "03_deploy_github_url.txt").write_text(
        url_str + ("\n" if url_str else ""),
        encoding="utf-8",
    )
    summary = {
        "out_dir": str(out),
        "markdown_chars": len(md),
        "deploy_github_url": url_str or None,
        "manus_provide_url_expected": bool(url_str),
    }
    (out / "02_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (out / "README.txt").write_text(
        "\n".join(
            [
                "Manus 工程テストのみ（デプロイは別スクリプト）",
                "",
                "次: python3 scripts/pipeline_test_deploy_only.py \\",
                f"    --url-file {out / '03_deploy_github_url.txt'}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"保存: {out}")
    print(f"markdown: {len(md)} chars")
    if url_str:
        print(f"deploy URL 行: {url_str[:80]}…" if len(url_str) > 80 else f"deploy URL: {url_str}")
    else:
        print("deploy URL: （空・MANUS が BOT_DEPLOY_GITHUB_URL を返さなかったか設定オフ）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
