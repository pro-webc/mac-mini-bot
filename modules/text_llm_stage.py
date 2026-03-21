"""TEXT_LLM 工程（要望抽出・仕様生成）。

現状は `llm_mock` に委譲。**実 LLM（API / CLI 等）を追加するときは主にこのモジュールを拡張する。**
"""
from __future__ import annotations

from typing import Any

from modules.basic_lp_text_llm import run_basic_lp_text_llm_pipeline
from modules.basic_text_llm import run_basic_text_llm_pipeline
from modules.case_extraction import ExtractedHearingBundle
from modules.advance_text_llm import run_advance_text_llm_pipeline
from modules.standard_text_llm import run_standard_text_llm_pipeline
from modules.contract_workflow import ContractWorkBranch, resolve_contract_work_branch
from modules.llm_mock import run_mock_text_llm_pipeline


def run_text_llm_stage(
    bundle: ExtractedHearingBundle,
    *,
    contract_plan: str,
    partner_name: str,
    work_branch: ContractWorkBranch | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    抽出済みヒアリングから `requirements_result` と `spec` を得る。

    Args:
        work_branch: 契約プランに応じた作業分岐。未指定時は ``contract_plan`` から解決する。

    Returns:
        (requirements_result, spec)
    """
    branch = work_branch or resolve_contract_work_branch(contract_plan)
    if branch == ContractWorkBranch.BASIC_LP:
        return run_basic_lp_text_llm_pipeline(
            hearing_sheet_content=bundle.hearing_sheet_content,
            appo_memo=bundle.appo_memo,
            sales_notes=bundle.sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
    if branch == ContractWorkBranch.BASIC:
        return run_basic_text_llm_pipeline(
            hearing_sheet_content=bundle.hearing_sheet_content,
            appo_memo=bundle.appo_memo,
            sales_notes=bundle.sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
    if branch == ContractWorkBranch.STANDARD:
        return run_standard_text_llm_pipeline(
            hearing_sheet_content=bundle.hearing_sheet_content,
            appo_memo=bundle.appo_memo,
            sales_notes=bundle.sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
    if branch == ContractWorkBranch.ADVANCE:
        return run_advance_text_llm_pipeline(
            hearing_sheet_content=bundle.hearing_sheet_content,
            appo_memo=bundle.appo_memo,
            sales_notes=bundle.sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
    return run_mock_text_llm_pipeline(
        hearing_sheet_content=bundle.hearing_sheet_content,
        appo_memo=bundle.appo_memo,
        sales_notes=bundle.sales_notes,
        contract_plan=contract_plan,
        partner_name=partner_name,
        work_branch=branch,
    )
