"""BASIC LP TEXT_LLM（モック）"""
import pytest

from modules.basic_lp_text_llm import run_basic_lp_text_llm_pipeline


def test_basic_lp_pipeline_single_page_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    # 実運用 .env でマニュアル有効でも、単体テストはモック経路に固定する
    monkeypatch.setattr("config.config.BASIC_LP_USE_GEMINI_MANUAL", False)
    req, spec = run_basic_lp_text_llm_pipeline(
        hearing_sheet_content="事業内容: 歯科クリニックの新規予約獲得。",
        appo_memo="メモ",
        sales_notes="営業所感",
        contract_plan="BASIC LP",
        partner_name="テスト歯科",
    )
    assert req["plan_type"] == "basic_lp"
    assert req["contract_max_pages"] == 1
    assert len(req["site_build_prompt"]) >= 400
    ps = spec.get("page_structure") or []
    assert len(ps) == 1
    assert ps[0].get("path") == "/"
    assert spec.get("site_overview", {}).get("site_name") == "テスト歯科"
    ux = spec.get("ux_spec") or {}
    assert ux.get("navigation_model") == "シングルページ（アンカーリンク）"
    assert spec.get("technical_spec", {}).get("common_requirements")
