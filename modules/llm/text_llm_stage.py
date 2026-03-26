"""TEXT_LLM 工程（要望抽出・仕様生成）。

プラン分岐は ``BRANCH_REGISTRY`` で一元管理。
``ContractWorkBranch`` を増やすときは ``modules.contract_workflow.BRANCH_REGISTRY`` に
エントリを追加すればこのモジュールの変更は不要。
"""
from __future__ import annotations

import importlib
import logging
from typing import Any

from config import config as cfg
from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import (
    BRANCH_REGISTRY,
    ContractWorkBranch,
    resolve_contract_work_branch,
)

from .llm_pipeline_common import require_claude_text_llm

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

    引数: bundle（フェーズ1 出力）/ contract_plan・partner_name（案件メタ）/ work_branch（省略時は自動解決）
    処理: BRANCH_REGISTRY からプラン設定を引き、対応する Claude CLI パイプラインを実行
    出力: (requirements_result, spec) — フェーズ3 以降の入力
    """
    branch = work_branch or resolve_contract_work_branch(contract_plan)
    branch_cfg = BRANCH_REGISTRY.get(branch)
    if branch_cfg is None:
        raise RuntimeError(
            f"未対応の作業分岐です: {branch!r}。"
            " modules.contract_workflow.BRANCH_REGISTRY にエントリを追加してください。"
        )

    require_claude_text_llm(
        manual_flag=getattr(cfg, branch_cfg.use_claude_flag),
        plan_label=branch_cfg.plan_label,
        manual_env_name=branch_cfg.use_claude_flag,
    )

    mod = importlib.import_module(branch_cfg.pipeline_module)
    pipeline_fn = getattr(mod, branch_cfg.pipeline_function)

    kw: dict[str, Any] = dict(
        hearing_sheet_content=bundle.hearing_sheet_content,
        appo_memo=bundle.appo_memo,
        sales_notes=bundle.sales_notes,
        contract_plan=contract_plan,
        partner_name=partner_name,
        record_number=record_number,
    )
    requirements_result, spec, _ = pipeline_fn(**kw)
    logger.info(
        "%s（Claude マニュアル）完了 plan_type=%s site_build_prompt_chars=%s",
        branch_cfg.plan_label,
        requirements_result.get("plan_type"),
        len(requirements_result.get("site_build_prompt") or ""),
    )
    return requirements_result, spec
