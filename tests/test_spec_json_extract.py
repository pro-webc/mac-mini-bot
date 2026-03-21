"""spec_json_extract の JSON 抽出。"""
from __future__ import annotations

import json

from modules.spec_json_extract import extract_spec_dict_from_llm_text


def test_extract_plain_json():
    d = {"site_overview": {"x": 1}, "a": 2}
    raw = json.dumps(d, ensure_ascii=False)
    got = extract_spec_dict_from_llm_text(raw)
    assert got == d


def test_extract_prose_then_json():
    prose = "第1段の要望を軸に整理しました。`page_structure` は `/` と `/about` です。\n\n"
    body = json.dumps({"site_overview": {"site_name": "T"}, "page_structure": []}, ensure_ascii=False)
    got = extract_spec_dict_from_llm_text(prose + body)
    assert got is not None
    assert got.get("site_overview", {}).get("site_name") == "T"


def test_extract_fenced_json():
    inner = json.dumps({"site_overview": {"k": 1}}, ensure_ascii=False)
    raw = f"説明です。\n```json\n{inner}\n```\n"
    got = extract_spec_dict_from_llm_text(raw)
    assert got is not None
    assert "site_overview" in got


def test_string_with_braces_inside():
    """JSON 文字列内の `{` がバランス崩しにしないこと。"""
    d = {
        "site_overview": {"hint": "use `{foo}` template"},
        "page_structure": [],
    }
    raw = "前置き\n" + json.dumps(d, ensure_ascii=False)
    got = extract_spec_dict_from_llm_text(raw)
    assert got == d


def test_no_json_returns_none():
    assert extract_spec_dict_from_llm_text("ただの文章です。") is None
