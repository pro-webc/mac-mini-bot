"""TEXT_LLM 工程（要望抽出・仕様生成）。

プラン分岐はこのモジュールの ``if/elif`` のみ。各分岐は
``require_gemini_text_llm`` のあと ``modules.*_gemini_manual`` のパイプラインを直接呼ぶ。
"""
from __future__ import annotations

import logging
from typing import Any

from config import config as cfg
from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import ContractWorkBranch, resolve_contract_work_branch

from .llm_pipeline_common import require_gemini_text_llm

logger = logging.getLogger(__name__)


def run_text_llm_stage(
    bundle: ExtractedHearingBundle,
    *,
    contract_plan: str,
    partner_name: str,
    record_number: str = "",
    work_branch: ContractWorkBranch | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    抽出済みヒアリングから ``requirements_result`` と ``spec`` を得る。

    ``ContractWorkBranch`` を増やしたら、この ``if/elif`` に分岐を追加する。
    """
    branch = work_branch or resolve_contract_work_branch(contract_plan)
    kw: dict[str, Any] = dict(
        hearing_sheet_content=bundle.hearing_sheet_content,
        appo_memo=bundle.appo_memo,
        sales_notes=bundle.sales_notes,
        contract_plan=contract_plan,
        partner_name=partner_name,
        record_number=record_number,
    )

    if branch == ContractWorkBranch.BASIC_LP:
        require_gemini_text_llm(
            manual_flag=cfg.BASIC_LP_USE_GEMINI_MANUAL,
            api_key=cfg.GEMINI_API_KEY,
            plan_label="BASIC LP TEXT_LLM",
            manual_env_name="BASIC_LP_USE_GEMINI_MANUAL",
        )
        from modules.basic_lp_gemini_manual import run_basic_lp_gemini_manual_pipeline

        requirements_result, spec, _ = run_basic_lp_gemini_manual_pipeline(**kw)
        logger.info(
            "BASIC LP TEXT_LLM（Gemini マニュアル）完了 plan_type=%s site_build_prompt_chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    if branch == ContractWorkBranch.BASIC:
        require_gemini_text_llm(
            manual_flag=cfg.BASIC_CP_USE_GEMINI_MANUAL,
            api_key=cfg.GEMINI_API_KEY,
            plan_label="BASIC TEXT_LLM",
            manual_env_name="BASIC_CP_USE_GEMINI_MANUAL",
        )
        from modules.basic_cp_gemini_manual import run_basic_cp_gemini_manual_pipeline

        requirements_result, spec, _ = run_basic_cp_gemini_manual_pipeline(**kw)
        logger.info(
            "BASIC TEXT_LLM（Gemini BASIC-CP マニュアル）完了 plan_type=%s site_build_prompt_chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    if branch == ContractWorkBranch.STANDARD:
        require_gemini_text_llm(
            manual_flag=cfg.STANDARD_CP_USE_GEMINI_MANUAL,
            api_key=cfg.GEMINI_API_KEY,
            plan_label="STANDARD TEXT_LLM",
            manual_env_name="STANDARD_CP_USE_GEMINI_MANUAL",
        )
        from modules.standard_cp_gemini_manual import run_standard_cp_gemini_manual_pipeline

        requirements_result, spec, _ = run_standard_cp_gemini_manual_pipeline(**kw)
        logger.info(
            "STANDARD TEXT_LLM（Gemini STANDARD-CP マニュアル）完了 plan_type=%s chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    if branch == ContractWorkBranch.ADVANCE:
        require_gemini_text_llm(
            manual_flag=cfg.ADVANCE_CP_USE_GEMINI_MANUAL,
            api_key=cfg.GEMINI_API_KEY,
            plan_label="ADVANCE TEXT_LLM",
            manual_env_name="ADVANCE_CP_USE_GEMINI_MANUAL",
        )
        from modules.advance_cp_gemini_manual import run_advance_cp_gemini_manual_pipeline

        requirements_result, spec, _ = run_advance_cp_gemini_manual_pipeline(**kw)
        logger.info(
            "ADVANCE TEXT_LLM（Gemini ADVANCE-CP マニュアル）完了 plan_type=%s chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    raise RuntimeError(
        f"未対応の作業分岐です: {branch!r}。"
        " ContractWorkBranch と modules.llm.text_llm_stage の if/elif を揃えてください。"
    )
