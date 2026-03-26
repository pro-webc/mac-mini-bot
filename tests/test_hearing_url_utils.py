"""modules.hearing_url_utils + claude_manual_common の URL 抽出テスト。

参考サイト URL 抽出は LLM 工程に移行済み。
ここでは残存するユーティリティ（既存サイト推定・デザイン excerpt・事実データ excerpt）と、
LLM 応答パースロジック（_parse_url_extraction_response / reference_url_block_from_extracted）を検証する。
"""
from __future__ import annotations

from modules import hearing_url_utils as u
from modules.claude_manual_common import (
    _parse_url_extraction_response,
    reference_url_block_from_extracted,
)


# ---------------------------------------------------------------------------
# 既存サイト URL 推定（Python ユーティリティ・LLM 不使用）
# ---------------------------------------------------------------------------


def test_existing_site_long_form_returns_empty() -> None:
    long = "x\n" * 200
    assert len(long) >= u.HEARING_PASTE_BODY_MIN_LEN
    assert u.existing_site_url_guess_from_hearing(long) == ""


def test_existing_site_short_cell_finds_url() -> None:
    assert (
        u.existing_site_url_guess_from_hearing("old site: https://old.example.jp/")
        == "https://old.example.jp/"
    )


# ---------------------------------------------------------------------------
# デザイン excerpt（キーワード行抽出・Python ユーティリティ）
# ---------------------------------------------------------------------------


def test_hearing_reference_design_excerpt_prefers_keyword_lines() -> None:
    body = (
        "会社名\n株式会社テスト\n\n"
        "希望する雰囲気のサイトのURLを教えてください。\n"
        "https://example.com/ref\n\n"
        "備考\nその他の行\n"
    )
    ex = u.hearing_reference_design_excerpt(body)
    assert "https://example.com/ref" in ex
    assert "希望する雰囲気" in ex


def test_hearing_reference_design_block_non_empty_when_hearing_empty() -> None:
    assert "再掲なし" in u.hearing_reference_design_block_for_prompt("")
    assert "下流でも必ず反映" in u.hearing_reference_design_block_for_prompt("配色は赤")


def test_design_excerpt_includes_extra_texts_design_lines() -> None:
    """extra_texts にデザイン関連キーワードがあれば excerpt に含まれる。"""
    hearing = "会社名\n株式会社テスト"
    sales = "配色はブルー系希望。高級感のあるデザインで"
    ex = u.hearing_reference_design_excerpt(hearing, extra_texts=[sales])
    assert "配色はブルー系希望" in ex or "高級感のあるデザイン" in ex


def test_design_block_with_extra_texts() -> None:
    """extra_texts を渡すと design block に反映される。"""
    block = u.hearing_reference_design_block_for_prompt(
        "会社概要テスト",
        extra_texts=["参考サイト https://example.com/ref デザインはモダンで"],
    )
    assert "下流でも必ず反映" in block
    assert "https://example.com/ref" in block or "モダン" in block


# ---------------------------------------------------------------------------
# 事実データ excerpt
# ---------------------------------------------------------------------------


def test_hearing_factual_block_contains_phone_line() -> None:
    body = "会社\n電話番号\n090-1234-5678\nデザイン\n赤系"
    block = u.hearing_factual_data_block_for_prompt(body)
    assert "欠落禁止" in block or "事実データ" in block
    assert "090-1234-5678" in block


def test_hearing_factual_block_empty() -> None:
    b = u.hearing_factual_data_block_for_prompt("")
    assert "再掲なし" in b or "参照" in b


# ---------------------------------------------------------------------------
# LLM 応答 JSON パース（_parse_url_extraction_response）
# ---------------------------------------------------------------------------


def test_parse_valid_json_array() -> None:
    raw = '```json\n[{"url": "https://a.com", "design_intent": "全体の雰囲気"}]\n```'
    result = _parse_url_extraction_response(raw)
    assert len(result) == 1
    assert result[0]["url"] == "https://a.com"
    assert result[0]["design_intent"] == "全体の雰囲気"


def test_parse_multiple_urls() -> None:
    raw = '[{"url":"https://a.com","design_intent":"配色"},{"url":"https://b.com","design_intent":"レイアウト"}]'
    result = _parse_url_extraction_response(raw)
    assert len(result) == 2
    assert result[0]["url"] == "https://a.com"
    assert result[1]["url"] == "https://b.com"


def test_parse_empty_array() -> None:
    assert _parse_url_extraction_response("[]") == []


def test_parse_no_json() -> None:
    assert _parse_url_extraction_response("参考サイトの記載はありません") == []


def test_parse_invalid_json() -> None:
    assert _parse_url_extraction_response("[{bad json}]") == []


def test_parse_skips_empty_url() -> None:
    raw = '[{"url": "", "design_intent": "なし"}, {"url": "https://valid.com", "design_intent": "参考"}]'
    result = _parse_url_extraction_response(raw)
    assert len(result) == 1
    assert result[0]["url"] == "https://valid.com"


def test_parse_defaults_design_intent() -> None:
    raw = '[{"url": "https://a.com"}]'
    result = _parse_url_extraction_response(raw)
    assert result[0]["design_intent"] == "参考サイト"


# ---------------------------------------------------------------------------
# reference_url_block_from_extracted（整形）
# ---------------------------------------------------------------------------


def test_block_from_extracted_empty() -> None:
    block = reference_url_block_from_extracted([])
    assert "記載なし" in block


def test_block_from_extracted_single() -> None:
    urls = [{"url": "https://a.com", "design_intent": "雰囲気参考"}]
    block = reference_url_block_from_extracted(urls)
    assert "https://a.com" in block
    assert "雰囲気参考" in block


def test_block_from_extracted_dedup() -> None:
    urls = [
        {"url": "https://a.com", "design_intent": "配色"},
        {"url": "https://a.com", "design_intent": "レイアウト"},
        {"url": "https://b.com", "design_intent": "参考"},
    ]
    block = reference_url_block_from_extracted(urls)
    assert block.count("https://a.com") == 1
    assert "https://b.com" in block
