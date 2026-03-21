#!/usr/bin/env python3
"""
本番と同じ経路で処理する（スプレッドシートから案件取得 → `WebsiteBot.process_case`）。

行わないことだけ本番と異なる:
  - Git への push、Vercel デプロイ、スプレッドシートのデプロイ URL / 完了系（AV・AW）の更新

各工程の出力は `preflight_artifact_dir` にまとめて保存される（`preflight_full.json` 等）。

  cd mac-mini-bot && .venv/bin/python scripts/run_preflight_before_push.py

- 起動検証は `main.py` と同様 `validate_startup_config(require_full_pipeline=True)`
- **既定: 本番と同じ `get_pending_cases()` でスプレッドシートから1件取得**（`PREFLIGHT_SOURCE` 未設定時）
- 任意: `PREFLIGHT_SHEET_ROW_NUMBER` / `PREFLIGHT_SHEET_CASE_INDEX`
- **擬似1行のみ試すとき**（非推奨・本番と異なる）: `PREFLIGHT_SOURCE=env` と
  `PREFLIGHT_PARTNER_NAME` / `PREFLIGHT_RECORD_NUMBER` / `PREFLIGHT_HEARING_SHEET_URL` 等
- **画像生成だけ省く**（当該実行のみ）: 実行前に `IMAGE_GEN_SKIP_RUN=1` を付与するか `.env` に一時設定（`main.py` の `--skip-images` と同等の効果）
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from config.config import SPREADSHEET_HEADERS_STRICT
from config.validation import validate_startup_config
from main import WebsiteBot

_PREFLIGHT_TOKEN = "__PREFLIGHT_OK__"


def _safe_dir_segment(s: str) -> str:
    t = (s or "").strip()
    if not t:
        return "unknown"
    t = re.sub(r'[/\\:\x00-\x1f<>:"|?*]', "-", t)
    t = t.strip(" .")
    return t or "unknown"


def _preflight_folder_name(record: str, partner: str) -> str:
    return f"test-{_safe_dir_segment(record)}-{_safe_dir_segment(partner)}"


def _preflight_uses_spreadsheet_case() -> bool:
    """
    既定 True: 本番と同じ `SpreadsheetClient.get_pending_cases()` で案件を取得する。
    明示的に `PREFLIGHT_SOURCE=env`（または synthetic / mock）のときだけ擬似行。
    """
    raw = (os.getenv("PREFLIGHT_SOURCE") or "sheet").strip().lower()
    if raw in ("env", "synthetic", "mock"):
        return False
    if raw in ("sheet", "1", "true", "yes", ""):
        return True
    raise ValueError(
        f"PREFLIGHT_SOURCE={raw!r} は未対応です。"
        "sheet（既定）または env / synthetic / mock のみ指定できます。"
    )


def _select_pending_case(spreadsheet: Any) -> dict[str, Any]:
    if SPREADSHEET_HEADERS_STRICT:
        mm = spreadsheet.validate_header_labels()
        if mm:
            raise RuntimeError("列見出し不一致: " + "; ".join(mm))

    cases = spreadsheet.get_pending_cases()
    if not cases:
        raise RuntimeError(
            "着手待ちの案件がありません（フェーズ・mac-mini 列・ヒアリング条件・必須列を確認）"
        )

    row_raw = os.getenv("PREFLIGHT_SHEET_ROW_NUMBER", "").strip()
    if row_raw:
        want = int(row_raw, 10)
        filtered = [c for c in cases if int(c["row_number"]) == want]
        if not filtered:
            raise RuntimeError(
                f"行 {want} は処理対象に含まれません（pending 行: "
                f'{[c["row_number"] for c in cases]}）'
            )
        cases = filtered

    idx_raw = os.getenv("PREFLIGHT_SHEET_CASE_INDEX", "0").strip() or "0"
    idx = int(idx_raw, 10)
    if idx < 0 or idx >= len(cases):
        raise RuntimeError(
            f"PREFLIGHT_SHEET_CASE_INDEX={idx} が範囲外です（0..{len(cases) - 1}）"
        )
    return cases[idx]


def _resolve_hearing_url_for_env_case() -> str:
    url_or_cell = os.getenv("PREFLIGHT_HEARING_SHEET_URL", "").strip()
    if url_or_cell:
        return url_or_cell
    body_file = os.getenv("PREFLIGHT_HEARING_SHEET_BODY_FILE", "").strip()
    if body_file:
        p = Path(body_file).expanduser()
        if not p.is_file():
            raise FileNotFoundError(
                f"PREFLIGHT_HEARING_SHEET_BODY_FILE が見つかりません: {p}"
            )
        return p.read_text(encoding="utf-8")
    return ""


def _build_env_synthetic_case() -> dict[str, Any]:
    partner = (
        os.getenv("PREFLIGHT_PARTNER_NAME", "テストパートナー株式会社").strip()
        or "テストパートナー株式会社"
    )
    record = os.getenv("PREFLIGHT_RECORD_NUMBER", "preflight-run").strip() or "preflight-run"
    hearing = _resolve_hearing_url_for_env_case()
    return {
        "row_number": 0,
        "record_number": record,
        "partner_name": partner,
        "contract_plan": os.getenv("PREFLIGHT_CONTRACT_PLAN", "").strip() or "STANDARD",
        "appo_memo": os.getenv("PREFLIGHT_APPO_MEMO", ""),
        "sales_notes": os.getenv("PREFLIGHT_SALES_NOTES", ""),
        "hearing_sheet_url": hearing,
        "ai_status": "",
        "phase_deadline": "",
        "test_site_url": "",
        "deploy_url": "",
    }


def main() -> int:
    result = validate_startup_config(require_full_pipeline=True)
    for w in result.warnings:
        print(f"WARN: {w}", flush=True)
    if not result.ok:
        for err in result.errors:
            print(f"ERROR: {err}", flush=True)
        return 1

    bot = WebsiteBot()

    if SPREADSHEET_HEADERS_STRICT:
        header_issues = bot.spreadsheet.validate_header_labels()
        if header_issues:
            for msg in header_issues:
                print(f"ERROR: [列見出し] {msg}", flush=True)
            return 1

    try:
        if _preflight_uses_spreadsheet_case():
            print(
                "=== 案件取得: スプレッドシート（本番と同じ get_pending_cases） ===",
                flush=True,
            )
            case = _select_pending_case(bot.spreadsheet)
        else:
            print(
                "WARN: PREFLIGHT_SOURCE=env — 擬似行です（本番の案件取得とは異なります）",
                flush=True,
            )
            case = _build_env_synthetic_case()
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", flush=True)
        return 1

    partner = (case.get("partner_name") or "").strip() or "unknown-partner"
    record = str(case.get("record_number") or "").strip() or "unknown-record"
    folder_name = _preflight_folder_name(record, partner)
    out_dir = ROOT / "output" / "preflight" / folder_name
    if out_dir.is_dir():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"=== プレフライト: WebsiteBot.process_case（各工程の出力を保存・Git push / デプロイ列更新はしない） ===",
        flush=True,
    )
    print(f"artifact_dir={out_dir}", flush=True)
    ret = bot.process_case(case, preflight_artifact_dir=out_dir)
    if ret == _PREFLIGHT_TOKEN:
        print(f"\n=== 成果物: {out_dir} ===", flush=True)
        print("=== done（GitHub / Vercel / デプロイ列は未実行）===", flush=True)
        return 0

    print("\n=== プレフライト失敗（preflight_full.json に途中経過あり）===", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
