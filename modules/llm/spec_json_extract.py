"""仕様書 LLM 応答から JSON オブジェクトを取り出す（前置き・```json フェンス対応）。"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


def _try_load_json_obj(blob: str) -> Optional[Dict[str, Any]]:
    blob = blob.strip()
    if not blob:
        return None
    try:
        val = json.loads(blob)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return val if isinstance(val, dict) else None


def _extract_fenced_json_blocks(text: str) -> List[str]:
    """```json ... ``` または ``` ... ``` の内側を列挙（出現順）。"""
    out: List[str] = []
    for m in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE):
        inner = (m.group(1) or "").strip()
        if inner:
            out.append(inner)
    return out


def _balanced_json_object_from(text: str, start_idx: int) -> Optional[str]:
    """start_idx 位置の `{` から、文字列内を考慮して対応する `}` までの部分文字列を返す。"""
    if start_idx < 0 or start_idx >= len(text) or text[start_idx] != "{":
        return None
    depth = 0
    i = start_idx
    in_string = False
    escape = False
    while i < len(text):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start_idx : i + 1]
        i += 1
    return None


def extract_spec_dict_from_llm_text(text: str) -> Optional[Dict[str, Any]]:
    """
    仕様書用のトップレベル JSON オブジェクトを抽出して dict にする。
    前置き日本語・マークダウン・```json フェンス内の JSON に対応。
    """
    if not (text or "").strip():
        return None

    raw = text.strip()

    # 1) 全体がそのまま JSON
    got = _try_load_json_obj(raw)
    if got is not None:
        return got

    # 2) フェンス内
    for block in _extract_fenced_json_blocks(text):
        got = _try_load_json_obj(block)
        if got is not None:
            return got
        jb = block.find("{")
        if jb != -1:
            inner = _balanced_json_object_from(block, jb)
            if inner:
                got = _try_load_json_obj(inner)
                if got is not None:
                    return got

    # 3) 文中の各 `{` からバランスマッチを試す
    starts: List[int] = []
    i = 0
    while i < len(text) and len(starts) < 48:
        j = text.find("{", i)
        if j == -1:
            break
        starts.append(j)
        i = j + 1

    for j in starts:
        blob = _balanced_json_object_from(text, j)
        if not blob:
            continue
        got = _try_load_json_obj(blob)
        if got is not None:
            return got

    return None
