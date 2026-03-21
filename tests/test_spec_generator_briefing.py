"""第2段・ブリーフテキスト組み立て"""
from modules.spec_generator import compose_spec_input_briefing


def test_compose_spec_input_briefing_has_core_sections() -> None:
    text = compose_spec_input_briefing(
        partner_name="テスト社",
        contract_plan="STANDARD",
        contract_pages=6,
        page_rule="複数ページで構成すること。",
        plan_info={"pages": 6, "name": "STANDARD"},
        hearing_sheet_content="ヒアリング本文",
        site_build_prompt="マスタープロンプト" * 50,
        requirements_result={
            "plan_type": "standard",
            "internal_build_notes": ["メモ1"],
            "open_questions": ["Q1"],
            "facts": {"key": ["a", "b"]},
        },
    )
    assert "【パートナー名】" in text
    assert "テスト社" in text
    assert "【ヒアリング原文】" in text
    assert "ヒアリング本文" in text
    assert "【第1段・サイト制作マスタープロンプト（最優先）】" in text
    assert "【第1段・内部メモ（サイト非掲載・参照のみ）】" in text
    assert "メモ1" in text
    assert "【要確認事項】" in text
    assert "Q1" in text
    assert "【第1段・補足ファクト（テキスト化）】" in text
