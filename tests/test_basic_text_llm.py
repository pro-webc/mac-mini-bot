"""BASIC プラン TEXT_LLM（Gemini マニュアル経路をスタブで検証）"""
import pytest
from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import ContractWorkBranch
from modules.llm.llm_pipeline_common import apply_common_technical_to_spec
from modules.llm.text_llm_stage import run_text_llm_stage


def test_basic_pipeline_single_page(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_cp(**kwargs: object) -> tuple[dict, dict, object]:
        req = {
            "plan_type": "basic",
            "site_build_prompt": "x" * 400,
            "contract_max_pages": 1,
            "internal_build_notes": [],
            "facts": {},
            "open_questions": [],
            "client_voice": "cv",
        }
        spec = apply_common_technical_to_spec(
            {
                "site_overview": {"site_name": "テスト商事"},
                "page_structure": [{"path": "/", "title": "トップ"}],
            }
        )
        return req, spec, object()

    monkeypatch.setattr("config.config.BASIC_CP_USE_GEMINI_MANUAL", True)
    monkeypatch.setattr("config.config.GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr(
        "modules.basic_cp_gemini_manual.run_basic_cp_gemini_manual_pipeline",
        fake_cp,
    )
    bundle = ExtractedHearingBundle(
        hearing_sheet_content="会社: テスト商事。事業: コンサル。",
        appo_memo="メモ",
        sales_notes="営業メモ",
    )
    req, spec = run_text_llm_stage(
        bundle,
        contract_plan="BASIC",
        partner_name="テスト商事",
        work_branch=ContractWorkBranch.BASIC,
    )
    assert req["plan_type"] == "basic"
    assert req["contract_max_pages"] == 1
    assert len(req["site_build_prompt"]) >= 400
    ps = spec.get("page_structure") or []
    assert len(ps) == 1
    assert ps[0].get("path") == "/"
    assert spec.get("technical_spec", {}).get("common_requirements")
