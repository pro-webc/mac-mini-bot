"""gemini_manual_common の共通ヘルパーテスト。"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from modules.gemini_manual_common import (
    existing_site_url_block,
    hearing_block,
    load_step,
    response_text,
    subst,
)


class TestSubst:
    def test_basic_replacement(self) -> None:
        assert subst("Hello {{NAME}}", NAME="World") == "Hello World"

    def test_multiple_placeholders(self) -> None:
        result = subst("{{A}} and {{B}}", A="1", B="2")
        assert result == "1 and 2"

    def test_unreplaced_raises(self) -> None:
        with pytest.raises(RuntimeError, match="プレースホルダが未置換"):
            subst("{{A}} and {{B}}", A="1")

    def test_module_name_in_error(self) -> None:
        with pytest.raises(RuntimeError, match="test_mod"):
            subst("{{X}}", module_name="test_mod")


class TestLoadStep:
    def test_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "step.txt"
        f.write_text("prompt text", encoding="utf-8")
        assert load_step(tmp_path, "step.txt") == "prompt text"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="マニュアルプロンプトが見つかりません"):
            load_step(tmp_path, "no_such_file.txt")


class TestHearingBlock:
    def test_valid(self) -> None:
        assert hearing_block("content") == "content"

    def test_empty_raises(self) -> None:
        with pytest.raises(RuntimeError, match="ヒアリングシート本文が空"):
            hearing_block("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(RuntimeError):
            hearing_block("   ")


class TestResponseText:
    def _make_response(self, text: str) -> MagicMock:
        part = MagicMock()
        part.text = text
        content = MagicMock()
        content.parts = [part]
        cand = MagicMock()
        cand.content = content
        cand.finish_reason = None
        resp = MagicMock()
        resp.candidates = [cand]
        return resp

    def test_extracts_text(self) -> None:
        resp = self._make_response("hello")
        assert response_text(resp) == "hello"

    def test_no_candidates_raises(self) -> None:
        resp = MagicMock()
        resp.candidates = []
        with pytest.raises(RuntimeError, match="candidates がありません"):
            response_text(resp)

    def test_empty_text_raises(self) -> None:
        resp = self._make_response("")
        with pytest.raises(RuntimeError, match="応答テキストが空"):
            response_text(resp)


class TestExistingSiteUrlBlock:
    def test_explicit_url(self) -> None:
        assert existing_site_url_block("hearing", "https://example.com") == "https://example.com"

    def test_empty_returns_fallback_message(self) -> None:
        result = existing_site_url_block("hearing without url", "")
        assert "既存サイトURL" in result
