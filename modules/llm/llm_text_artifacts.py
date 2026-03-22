"""LLM 由来データを UTF-8 テキスト（主に YAML）で保存・埋め込む。

ディスク上の正本や、台本へのフォールバック文字列は JSON ではなく人間可読なテキストに揃える。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def yaml_dump_llm_data(data: Any) -> str:
    """構造化データを YAML ブロック（UTF-8 で書ける文字列）にする。"""
    text = yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_llm_yaml_artifact(path: Path, data: Any) -> None:
    """LLM 関連の構造化データを 1 ファイルの YAML テキストとして保存する。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_dump_llm_data(data), encoding="utf-8")


def requirements_dict_as_llm_fallback_text(
    requirements_result: dict[str, Any],
    *,
    max_chars: int = 8000,
) -> str:
    """site_build_prompt が空のとき、台本へ埋め込む要約（テキスト形式・既定は YAML）。"""
    blob = yaml_dump_llm_data(requirements_result)
    if len(blob) <= max_chars:
        return blob
    return blob[: max_chars - 1] + "…"
