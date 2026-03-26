"""本番 ``main`` と同じ手順で ``process_case`` 直前まで進み、各段の出力を保存する。"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import (
    BOT_MAX_CASES,
    pipeline_preflight_snapshots_base,
)
from config.logging_setup import configure_logging
from config.validation import validate_startup_config

configure_logging()

from main import (
    WebsiteBot,
    _emit_startup_validation,
)


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def snapshot_preflight_before_process_case(
    *,
    output_root: Path | None = None,
) -> Path:
    """
    起動検証 → ``WebsiteBot`` → 列自動検出 → ``get_pending_cases`` → ``main.run()`` と同じ
    ``BOT_MAX_CASES`` による先頭 N 件切り詰めまで実行し、各結果を JSON で保存する。
    ``process_case`` は呼ばない。

    本番で 1 件実行する場合とキューを揃えるには、実行時に ``BOT_MAX_CASES=1`` を付ける（または
    ``.env`` に同値を設定する）。

    本番と同じ失敗時挙動（設定 NG・列検出失敗なら例外→ ``sys.exit(1)``）。

    Returns:
        保存先ディレクトリ
    """
    base = output_root or pipeline_preflight_snapshots_base()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base / stamp
    out.mkdir(parents=True, exist_ok=True)

    cfg_result = validate_startup_config(require_full_pipeline=True)
    _write_json(
        out / "01_startup_validation.json",
        {
            "ok": cfg_result.ok,
            "warnings": list(cfg_result.warnings),
            "errors": list(cfg_result.errors),
        },
    )
    if not _emit_startup_validation(cfg_result, to_stdout=False):
        sys.exit(1)

    bot = WebsiteBot()
    _write_json(
        out / "02_resolved_columns.json",
        {
            "columns": dict(sorted(bot.spreadsheet.columns.items())),
        },
    )

    cases = bot.spreadsheet.get_pending_cases()
    original_count = len(cases)
    if BOT_MAX_CASES:
        cases = cases[:BOT_MAX_CASES]

    _write_json(
        out / "03_pending_cases_summary.json",
        {
            "fetched_count": original_count,
            "after_bot_max_cases": len(cases),
            "bot_max_cases": BOT_MAX_CASES or None,
        },
    )
    _write_json(out / "04_pending_cases.json", _json_safe(cases))

    (out / "README.txt").write_text(
        "\n".join(
            [
                "preflight スナップショット（process_case 直前まで）",
                "",
                "01_startup_validation.json — validate_startup_config の結果",
                "02_resolved_columns.json — 1行目の見出しから自動検出した列位置マッピング",
                "03_pending_cases_summary.json — get_pending_cases の件数と BOT_MAX_CASES",
                "04_pending_cases.json — BOT_MAX_CASES 適用後の案件（main.run() がループするリストと同じ）",
                "",
                "本番で 1 件だけ試すときは BOT_MAX_CASES=1 を付けて本スクリプトを実行すると、",
                "04 の内容が python main.py（同じ BOT_MAX_CASES）の process_case 対象と一致します。",
                "",
                "本番 main では続けて WebsiteBot.run() が各案件で process_case を呼びます。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out
