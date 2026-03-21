"""BASIC プラン TEXT_LLM（モック）"""
import pytest

from modules.basic_text_llm import run_basic_text_llm_pipeline


def test_basic_pipeline_single_page(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("config.config.BASIC_CP_USE_GEMINI_MANUAL", False)
    req, spec = run_basic_text_llm_pipeline(
        hearing_sheet_content="会社: テスト商事。事業: コンサル。",
        appo_memo="メモ",
        sales_notes="営業メモ",
        contract_plan="BASIC",
        partner_name="テスト商事",
    )
    assert req["plan_type"] == "basic"
    assert req["contract_max_pages"] == 1
    assert len(req["site_build_prompt"]) >= 400
    ps = spec.get("page_structure") or []
    assert len(ps) == 1
    assert ps[0].get("path") == "/"
    assert spec.get("technical_spec", {}).get("common_requirements")
