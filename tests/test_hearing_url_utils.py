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
