"""第1段プレーンテキスト応答の正規化"""
import pytest
from modules.llm_mock import (
    finalize_plain_prompt as _finalize_plain_prompt,
)
from modules.llm_mock import (
    unwrap_plaintext_llm_output as _unwrap_plaintext_llm_output,
)


def test_unwrap_plaintext_strips_outer_fence() -> None:
    raw = """```text
Line one
Line two
```"""
    assert _unwrap_plaintext_llm_output(raw) == "Line one\nLine two"


def test_unwrap_plaintext_no_fence() -> None:
    assert _unwrap_plaintext_llm_output("  hello  ") == "hello"


def test_finalize_plain_prompt_too_short() -> None:
    with pytest.raises(RuntimeError, match="短すぎ"):
        _finalize_plain_prompt("x" * 50, expected_plan_type="standard", max_pages=6)


def test_finalize_plain_prompt_ok() -> None:
    body = "あ" * 500
    out = _finalize_plain_prompt(body, expected_plan_type="standard", max_pages=6)
    assert out["plan_type"] == "standard"
    assert out["site_build_prompt"] == body
    assert out["contract_max_pages"] == 6
    assert out["facts"] == {}
    assert out["client_voice"] == body[:2000]
