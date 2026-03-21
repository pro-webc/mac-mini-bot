"""TEXT_LLM 工程（要望抽出・仕様生成）。

現状は `llm_mock` に委譲。**実 LLM（API / CLI 等）を追加するときは主にこのモジュールを拡張する。**
"""
from __future__ import annotations

from typing import Any

from modules.case_extraction import ExtractedHearingBundle
from modules.llm_mock import run_mock_text_llm_pipeline


def run_text_llm_stage(
    bundle: ExtractedHearingBundle,
    *,
    contract_plan: str,
    partner_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    抽出済みヒアリングから `requirements_result` と `spec` を得る。

    Returns:
        (requirements_result, spec)
    """
    return run_mock_text_llm_pipeline(
        hearing_sheet_content=bundle.hearing_sheet_content,
        appo_memo=bundle.appo_memo,
        sales_notes=bundle.sales_notes,
        contract_plan=contract_plan,
        partner_name=partner_name,
    )
