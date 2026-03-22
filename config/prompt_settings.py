"""共通プロンプト（`config/prompts/common/*.txt`）を UTF-8 テキストとして読み込む。

- 生成パイプラインへの自動マージは行わない。参照されるのは主に
  `get_technical_spec_prompt_block()`（仕様・実装向けの技術要件テキスト）。
- 編集はエディタにそのまま貼り付け・追記できるプレーン UTF-8 テキスト。

プレースホルダーは `{name}`（`format_prompt` / `apply_prompt_template` 利用時）。
差し込み値に `{` を含めないこと（誤置換防止）。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_CONFIG_DIR = Path(__file__).resolve().parent
_PROMPTS_DIR = _CONFIG_DIR / "prompts"
_COMMON_DIR = _PROMPTS_DIR / "common"
_TECH_SPEC_TXT = _COMMON_DIR / "technical_spec_prompt_block.txt"


@lru_cache(maxsize=1)
def _read_technical_spec_prompt_block_raw() -> str:
    if not _PROMPTS_DIR.is_dir():
        raise FileNotFoundError(
            f"プロンプトディレクトリが見つかりません: {_PROMPTS_DIR}"
        )
    if not _COMMON_DIR.is_dir():
        raise FileNotFoundError(
            f"config/prompts/common/ が必要です: {_COMMON_DIR}"
        )
    if not _TECH_SPEC_TXT.is_file():
        raise FileNotFoundError(
            f"技術要件テキストが見つかりません（UTF-8 .txt を配置してください）: {_TECH_SPEC_TXT}"
        )
    return _TECH_SPEC_TXT.read_text(encoding="utf-8")


def clear_prompt_cache() -> None:
    """テストやホットリロード用（通常運用では不要）。"""
    _read_technical_spec_prompt_block_raw.cache_clear()


def get_prompt_str(key_path: str) -> str:
    """現状は `common.technical_spec_prompt_block` のみ（テキストファイルの内容）。"""
    if key_path == "common.technical_spec_prompt_block":
        return _read_technical_spec_prompt_block_raw()
    raise KeyError(
        f"prompt_settings にキーがありません: {key_path!r} "
        f"（利用可能: 'common.technical_spec_prompt_block'）"
    )


def apply_prompt_template(template: str, **kwargs: Any) -> str:
    out = template
    for k, v in kwargs.items():
        out = out.replace("{" + k + "}", v if isinstance(v, str) else str(v))
    return out


def format_prompt(template_key_path: str, **kwargs: Any) -> str:
    tpl = get_prompt_str(template_key_path)
    return apply_prompt_template(tpl, **kwargs)


def get_technical_spec_prompt_block() -> str:
    """LLM プロンプト用の技術要件テキスト（旧 config.get_common_technical_spec_prompt_block と同一役割）。"""
    return get_prompt_str("common.technical_spec_prompt_block").rstrip() + "\n"
