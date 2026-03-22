"""ヒアリング取得（fetch_hearing_sheet）の HTML→テキスト化"""
from __future__ import annotations

from typing import Any

import pytest
from modules import spec_generator as sg
from modules.hearing_url_utils import HEARING_PASTE_BODY_MIN_LEN


def test_html_to_plain_text_strips_tags_and_scripts() -> None:
    html = (
        "<!DOCTYPE html><html><head><title>T</title></head>"
        "<body><p>  Hello  </p><script>evil()</script>"
        "<style>.x{}</style><noscript>n</noscript>World</body></html>"
    )
    out = sg._html_to_plain_text(html)
    assert "<" not in out
    assert "evil" not in out
    assert "Hello" in out
    assert "World" in out


def test_http_response_as_plain_text_html_ct() -> None:
    class Resp:
        text = "<html><body><p>Line1</p><p>Line2</p></body></html>"
        headers = {"Content-Type": "text/html; charset=utf-8"}

    plain = sg._http_response_as_plain_text(Resp())  # type: ignore[arg-type]
    assert "<p>" not in plain
    assert "Line1" in plain
    assert "Line2" in plain


def test_http_response_as_plain_text_json_unchanged() -> None:
    class Resp:
        text = '{"a": 1}'
        headers = {"Content-Type": "application/json"}

    assert sg._http_response_as_plain_text(Resp()) == '{"a": 1}'  # type: ignore[arg-type]


def test_maybe_strip_html_pasted_text_plain_unchanged() -> None:
    s = "今回広告サイトで紹介する\n正式名称を教えてください。"
    assert sg._maybe_strip_html_pasted_text(s) == s


@pytest.fixture
def fake_get_html(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resp:
        status_code = 200
        text = "<html><body><h1>フォーム回答</h1><p>本文</p></body></html>"
        headers: dict[str, str] = {"Content-Type": "text/html; charset=utf-8"}

    def get(*_a: Any, **_k: Any) -> Resp:
        return Resp()

    monkeypatch.setattr(sg.requests, "get", get)


def test_fetch_hearing_sheet_long_paste_does_not_fetch_embedded_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """質問票コピペの途中に参考URLがあっても、外部ページを取りに行かない。"""

    def boom(*_a: Any, **_k: Any) -> None:
        raise AssertionError("長文セルでは requests.get してはいけない")

    monkeypatch.setattr(sg.requests, "get", boom)
    gen = sg.SpecGenerator()
    body = ("質問\n回答\n" * 120) + "https://example.com/reference\n"
    assert len(body) >= HEARING_PASTE_BODY_MIN_LEN
    out = gen.fetch_hearing_sheet(body)
    assert out
    assert "https://example.com/reference" in out
    assert "質問" in out


def test_fetch_hearing_sheet_generic_url_returns_plain_text(
    fake_get_html: None,
) -> None:
    gen = sg.SpecGenerator()
    out = gen.fetch_hearing_sheet("https://example.com/hearing")
    assert out
    assert "<html" not in (out or "").lower()
    assert "フォーム回答" in (out or "")
    assert "本文" in (out or "")
