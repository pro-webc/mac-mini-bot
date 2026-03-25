"""modules.hearing_url_utils（ヒアリング列の URL 解釈の共有）"""
from __future__ import annotations

from modules import hearing_url_utils as u


def test_reference_site_prefers_labeled_line_in_long_form() -> None:
    filler = "補足行\n" * 80
    body = (
        "会社名\n株式会社テスト\n\n"
        + filler
        + "希望する雰囲気のサイトのURLを教えてください。\n"
        "https://example.com/want-this\n\n"
        "その他\nhttps://example.com/other\n"
    )
    assert len(body) >= u.HEARING_PASTE_BODY_MIN_LEN
    assert u.reference_site_url_from_hearing(body) == "https://example.com/want-this"


def test_reference_site_short_cell_first_url() -> None:
    assert (
        u.reference_site_url_from_hearing("see https://a.com and https://b.com")
        == "https://a.com"
    )


def test_existing_site_long_form_returns_empty() -> None:
    long = "x\n" * 200
    assert len(long) >= u.HEARING_PASTE_BODY_MIN_LEN
    assert u.existing_site_url_guess_from_hearing(long) == ""


def test_existing_site_short_cell_finds_url() -> None:
    assert (
        u.existing_site_url_guess_from_hearing("old site: https://old.example.jp/")
        == "https://old.example.jp/"
    )


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


def test_reference_site_url_from_extra_texts_sales_notes() -> None:
    """ヒアリング本文に URL がなくても sales_notes から参考サイト URL を取得できる。"""
    hearing = "会社名\n株式会社テスト\n強み\n安い"
    sales = "この参考サイトをもとに https://www.coralshareclub.com/ 寄せて作ってください"
    result = u.reference_site_url_from_hearing(hearing, extra_texts=[sales])
    assert result == "https://www.coralshareclub.com/"


def test_reference_site_url_hearing_takes_priority_over_extra() -> None:
    """ヒアリング本文に URL がある場合は extra_texts より優先される。"""
    hearing = "参考 https://hearing.example.com"
    sales = "参考サイト https://sales.example.com"
    result = u.reference_site_url_from_hearing(hearing, extra_texts=[sales])
    assert result == "https://hearing.example.com"


def test_reference_site_url_long_hearing_no_url_falls_back_to_extra() -> None:
    """長文ヒアリングで「希望するURL」が空のとき、extra_texts へフォールバックする。"""
    filler = "補足行\n" * 120
    hearing = (
        "会社名\n株式会社テスト\n\n"
        + filler
        + "希望する雰囲気のサイトのURLを教えてください。\n"
        "記入しない\n\n"
    )
    assert len(hearing) >= u.HEARING_PASTE_BODY_MIN_LEN
    sales = "参考サイト https://ref-from-sales.example.com に寄せる"
    result = u.reference_site_url_from_hearing(hearing, extra_texts=[sales])
    assert result == "https://ref-from-sales.example.com"


def test_design_excerpt_includes_extra_texts_design_lines() -> None:
    """extra_texts にデザイン関連キーワードがあれば excerpt に含まれる。"""
    hearing = "会社名\n株式会社テスト"
    sales = "配色はブルー系希望。高級感のあるデザインで"
    ex = u.hearing_reference_design_excerpt(hearing, extra_texts=[sales])
    assert "配色はブルー系希望" in ex or "高級感のあるデザイン" in ex


def test_hearing_factual_block_contains_phone_line() -> None:
    body = "会社\n電話番号\n090-1234-5678\nデザイン\n赤系"
    block = u.hearing_factual_data_block_for_prompt(body)
    assert "欠落禁止" in block or "事実データ" in block
    assert "090-1234-5678" in block


def test_hearing_factual_block_empty() -> None:
    b = u.hearing_factual_data_block_for_prompt("")
    assert "再掲なし" in b or "参照" in b


def test_design_block_with_extra_texts() -> None:
    """extra_texts を渡すと design block に反映される。"""
    block = u.hearing_reference_design_block_for_prompt(
        "会社概要テスト",
        extra_texts=["参考サイト https://example.com/ref デザインはモダンで"],
    )
    assert "下流でも必ず反映" in block
    assert "https://example.com/ref" in block or "モダン" in block
