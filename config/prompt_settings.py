"""LLM 用プロンプト（`config/prompts/<工程名>/*.yaml`）の読み込みとプレースホルダ差し込み。

- 各 **サブディレクトリ名** がマージ後のトップレベルキー（例: `text_llm/default.yaml` → `text_llm.default_system`）。
- 同一工程フォルダ内の複数 YAML は **深いマージ**（後ろのファイルがキーを上書き）。

プレースホルダーは `{name}`。差し込み値に `{` を含めないこと（誤置換防止）。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent
_PROMPTS_DIR = _CONFIG_DIR / "prompts"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    if not _PROMPTS_DIR.is_dir():
        raise FileNotFoundError(
            f"プロンプトディレクトリが見つかりません: {_PROMPTS_DIR}"
        )
    merged: dict[str, Any] = {}
    stage_dirs = sorted(
        p for p in _PROMPTS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if not stage_dirs:
        raise FileNotFoundError(
            f"工程フォルダがありません（config/prompts/<工程名>/ を作成してください）: {_PROMPTS_DIR}"
        )
    for stage_dir in stage_dirs:
        name = stage_dir.name
        if name == "__pycache__":
            continue
        stage_blob: dict[str, Any] = {}
        yaml_paths = sorted(stage_dir.glob("*.yaml"))
        if not yaml_paths:
            raise FileNotFoundError(
                f"プロンプト YAML がありません: {stage_dir}（*.yaml を1つ以上置いてください）"
            )
        for path in yaml_paths:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data is None:
                data = {}
            if not isinstance(data, dict):
                raise ValueError(
                    f"プロンプトファイルのルートはマッピングである必要があります: {path}"
                )
            stage_blob = _deep_merge(stage_blob, data)
        if name in merged:
            raise ValueError(f"プロンプト工程名の重複: {name!r}")
        merged[name] = stage_blob
    return merged


def clear_prompt_cache() -> None:
    """テストやホットリロード用（通常運用では不要）。"""
    _load_raw.cache_clear()


def _get_nested(key_path: str) -> Any:
    cur: Any = _load_raw()
    for part in key_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(
                f"prompt_settings にキーがありません: {key_path!r} (失敗セグメント: {part!r})"
            )
        cur = cur[part]
    return cur


def get_prompt_str(key_path: str) -> str:
    v = _get_nested(key_path)
    if not isinstance(v, str):
        raise TypeError(f"prompt_settings.{key_path} は文字列である必要があります（実際: {type(v)!r}）")
    return v


def apply_prompt_template(template: str, **kwargs: Any) -> str:
    out = template
    for k, v in kwargs.items():
        out = out.replace("{" + k + "}", v if isinstance(v, str) else str(v))
    return out


def format_prompt(template_key_path: str, **kwargs: Any) -> str:
    tpl = get_prompt_str(template_key_path)
    return apply_prompt_template(tpl, **kwargs)


def get_text_llm_default_system() -> str:
    return get_prompt_str("text_llm.default_system")


def get_technical_spec_prompt_block() -> str:
    """LLM プロンプト用の技術要件テキスト（旧 config.get_common_technical_spec_prompt_block と同一役割）。"""
    return get_prompt_str("common.technical_spec_prompt_block").rstrip() + "\n"
