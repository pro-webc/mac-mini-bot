"""llm_pipeline_common（プレーンテキスト正規化・要望 dict 整形）"""
import pytest
from modules.llm.llm_pipeline_common import (
    finalize_plain_prompt,
    require_gemini_text_llm,
    unwrap_plaintext_llm_output,
)


def test_unwrap_plaintext_strips_outer_fence() -> None:
    raw = """```text
Line one
Line two
```"""
    assert unwrap_plaintext_llm_output(raw) == "Line one\nLine two"


def test_unwrap_plaintext_no_fence() -> None:
    assert unwrap_plaintext_llm_output("  hello  ") == "hello"


def test_finalize_plain_prompt_too_short() -> None:
    with pytest.raises(RuntimeError, match="短すぎ"):
        finalize_plain_prompt("x" * 50, expected_plan_type="standard", max_pages=6)


def test_require_gemini_text_llm_raises_when_disabled() -> None:
    with pytest.raises(RuntimeError, match="Gemini マニュアルが無効"):
        require_gemini_text_llm(
            manual_flag=False,
            api_key="x",
            plan_label="TEST",
            manual_env_name="TEST_USE_GEMINI_MANUAL",
        )


def test_require_gemini_text_llm_ok() -> None:
    require_gemini_text_llm(
        manual_flag=True,
        api_key="sk-test",
        plan_label="TEST",
        manual_env_name="TEST_USE_GEMINI_MANUAL",
    )


def test_finalize_plain_prompt_ok() -> None:
    body = "あ" * 500
    out = finalize_plain_prompt(body, expected_plan_type="standard", max_pages=6)
    assert out["plan_type"] == "standard"
    assert out["site_build_prompt"] == body
    assert out["contract_max_pages"] == 6
    assert out["facts"] == {}
    assert out["client_voice"] == body[:2000]
