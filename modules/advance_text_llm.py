"""ADVANCE（コーポレート・12ページ）契約向け TEXT_LLM 工程。

- ``ADVANCE_CP_USE_GEMINI_MANUAL``: ``modules.advance_cp_gemini_manual``（16回 + 任意リファクタ）
- それ以外: ``llm_mock``（plan_type=advance・ページ数は契約プランに従う）
"""
from __future__ import annotations

import logging
from typing import Any

from modules.llm_mock import (
    build_requirements_result_mock,
    build_spec_dict_mock,
)

logger = logging.getLogger(__name__)


def build_advance_spec_dict(
    requirements_result: dict[str, Any],
    contract_plan: str,
    partner_name: str,
    *,
    hearing_sheet_content: str,
) -> dict[str, Any]:
    """仕様 dict（ADVANCE 向け・``build_spec_dict_mock`` に委譲）。"""
    return build_spec_dict_mock(
        hearing_sheet_content,
        requirements_result,
        contract_plan,
        partner_name,
    )


def run_advance_text_llm_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    ADVANCE 向け要望整理 + 仕様生成。

    Returns:
        (requirements_result, spec)
    """
    from config.config import ADVANCE_CP_USE_GEMINI_MANUAL, GEMINI_API_KEY

    if ADVANCE_CP_USE_GEMINI_MANUAL and (GEMINI_API_KEY or "").strip():
        from modules.advance_cp_gemini_manual import run_advance_cp_gemini_manual_pipeline

        requirements_result, spec, _ = run_advance_cp_gemini_manual_pipeline(
            hearing_sheet_content=hearing_sheet_content,
            appo_memo=appo_memo,
            sales_notes=sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
        logger.info(
            "ADVANCE TEXT_LLM（Gemini ADVANCE-CP マニュアル）完了 plan_type=%s chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    requirements_result = build_requirements_result_mock(
        hearing_sheet_content,
        appo_memo,
        sales_notes,
        contract_plan,
    )
    spec = build_spec_dict_mock(
        hearing_sheet_content,
        requirements_result,
        contract_plan,
        partner_name,
    )
    logger.info(
        "ADVANCE TEXT_LLM（モック）完了 plan_type=%s",
        requirements_result.get("plan_type"),
    )
    return requirements_result, spec
