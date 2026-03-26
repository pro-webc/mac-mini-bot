"""BASIC LP TEXT_LLM（Claude CLI マニュアル経路をスタブで検証）"""
import pytest
from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import ContractWorkBranch
from modules.llm.llm_pipeline_common import apply_common_technical_to_spec
from modules.llm.text_llm_stage import run_text_llm_stage


def test_basic_lp_pipeline_single_page_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_lp(**kwargs: object) -> tuple[dict, dict, object]:
        req = {
            "plan_type": "basic_lp",
            "site_build_prompt": "y" * 400,
            "contract_max_pages": 1,
            "internal_build_notes": [],
            "facts": {},
            "open_questions": [],
            "client_voice": "cv",
        }
        spec = apply_common_technical_to_spec(
            {
                "site_overview": {"site_name": "テスト歯科"},
                "page_structure": [{"path": "/", "title": "ランディング"}],
                "ux_spec": {"navigation_model": "シングルページ（アンカーリンク）"},
            }
        )
        return req, spec, object()

    monkeypatch.setattr("config.config.BASIC_LP_USE_CLAUDE_MANUAL", True)
    monkeypatch.setattr(
        "modules.basic_lp_claude_manual.run_basic_lp_claude_manual_pipeline",
        fake_lp,
    )
    bundle = ExtractedHearingBundle(
        hearing_sheet_content="事業内容: 歯科クリニックの新規予約獲得。",
        appo_memo="メモ",
        sales_notes="営業所感",
    )
    req, spec = run_text_llm_stage(
        bundle,
        contract_plan="BASIC LP",
        partner_name="テスト歯科",
        work_branch=ContractWorkBranch.BASIC_LP,
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
