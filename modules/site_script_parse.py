"""第2段 LLM 応答: Markdown サイト台本 + 末尾 ```yaml``` メタのパース（レガシー JSON 仕様との互換）。"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

import yaml

from modules.spec_json_extract import extract_spec_dict_from_llm_text

_YAML_FENCE_RE = re.compile(
    r"```(?:yaml|yml)\s*([\s\S]*?)```",
    re.IGNORECASE,
)


def extract_last_yaml_fence(text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    文中の最後の ```yaml ... ``` を取り除いた本文と、パース済み dict を返す。
    yaml が無い・パース不能なら meta は None（本文は元テキストの strip）。
    """
    raw = (text or "").strip()
    if not raw:
        return "", None
    matches = list(_YAML_FENCE_RE.finditer(raw))
    if not matches:
        return raw, None
    last = matches[-1]
    inner = (last.group(1) or "").strip()
    try:
        meta = yaml.safe_load(inner)
    except (yaml.YAMLError, TypeError, ValueError):
        return raw, None
    if not isinstance(meta, dict):
        return raw, None
    before = raw[: last.start()].rstrip()
    after = raw[last.end() :].lstrip()
    body = f"{before}\n\n{after}".strip() if after else before.strip()
    return body, meta


def _build_spec_from_script_meta(body: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    overview = meta.get("site_overview")
    if not isinstance(overview, dict):
        raise ValueError("YAML に site_overview（オブジェクト）が必須です")
    site_name = overview.get("site_name")
    if not isinstance(site_name, str) or not site_name.strip():
        raise ValueError("site_overview.site_name（非空文字列）が必須です")

    design = meta.get("design_spec")
    if not isinstance(design, dict):
        design = {}
    colors = design.get("color_scheme") or design.get("tokens")
    if not isinstance(colors, dict) or not colors:
        raise ValueError("design_spec.color_scheme（または tokens）に少なくとも1キーが必須です")

    if len(body.strip()) < 80:
        raise ValueError("YAML フェンス以外の Markdown 本文が短すぎます（最低約80文字）")

    out: Dict[str, Any] = {
        "site_script_md": body.strip(),
        "site_overview": overview,
        "design_spec": design,
        "content_spec": meta.get("content_spec") if isinstance(meta.get("content_spec"), dict) else {},
        "page_structure": meta.get("page_structure") if isinstance(meta.get("page_structure"), list) else [],
        "ux_spec": meta.get("ux_spec") if isinstance(meta.get("ux_spec"), dict) else {},
        "function_spec": meta.get("function_spec") if isinstance(meta.get("function_spec"), dict) else {},
        "image_placeholder_slots": meta.get("image_placeholder_slots")
        if isinstance(meta.get("image_placeholder_slots"), list)
        else [],
    }
    if isinstance(meta.get("technical_spec"), dict):
        out["technical_spec"] = meta["technical_spec"]
    return out


def parse_llm_spec_or_site_script(raw: str) -> Tuple[Dict[str, Any], str]:
    """
    LLM 応答を仕様 dict に統一する。

    Returns:
        (spec_dict, mode)  mode は "legacy_json" | "site_script"

    優先順: 有効な末尾 YAML メタ → 先頭 `{` の JSON → 埋め込み JSON（page_structure キーあり）。
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("LLM 応答が空です")

    body, meta = extract_last_yaml_fence(s)
    if meta is not None:
        try:
            return _build_spec_from_script_meta(body, meta), "site_script"
        except ValueError:
            pass  # 不完全な YAML の可能性 → レガシー JSON を試す

    if s.startswith("{"):
        data = extract_spec_dict_from_llm_text(raw)
        if isinstance(data, dict) and data.get("site_overview"):
            return data, "legacy_json"

    data = extract_spec_dict_from_llm_text(raw)
    if isinstance(data, dict) and data.get("site_overview") and "page_structure" in data:
        return data, "legacy_json"

    if meta is not None:
        # YAML はあったが _build で失敗していた
        raise ValueError(
            "末尾の ```yaml``` はパースできましたが、site_overview.site_name・design_spec.color_scheme 等が不足しています"
        )
    raise ValueError(
        "応答の末尾に ```yaml ... ```（site_overview / design_spec を含む）を付けるか、"
        "従来どおり仕様書 JSON 1 本で出力してください"
    )
