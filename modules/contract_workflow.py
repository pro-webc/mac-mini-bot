"""スプレッドシートの契約プラン（plan_type 列）に応じた作業分岐の解決。

``BRANCH_REGISTRY`` が全プランの設定を一元管理する。
新プラン追加はここにエントリを足すだけで、散在 dict / if-elif を個別に修正する必要がない。
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from config.config import get_contract_plan_info


class ContractWorkBranch(str, Enum):
    """契約プランに対応する作業パイプライン種別。"""

    BASIC_LP = "basic_lp"
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCE = "advance"


# ---------------------------------------------------------------------------
# BranchConfig: プラン固有情報の Single Source of Truth
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BranchConfig:
    """ContractWorkBranch に紐づくプラン固有の定数一式。

    ``config.config`` のフラグ名は文字列で参照し、循環 import を避ける。
    """

    refactor_key: str
    canvas_key: str
    manual_meta_key: str
    extra_spec_keys: tuple[str, ...]
    use_gemini_flag: str
    refactor_flag: str
    plan_label: str
    pipeline_module: str
    pipeline_function: str

    @property
    def manus_keys(self) -> tuple[str, str]:
        """(リファクタ出力キー, Gemini Canvas キー) — Manus 前後で参照。"""
        return (self.refactor_key, self.canvas_key)

    @property
    def spec_llm_keys(self) -> tuple[str, ...]:
        """spec に載りうる LLM テキストキーの全量（llm_raw_output 書き出し用）。"""
        return (
            self.refactor_key,
            self.canvas_key,
            *self.extra_spec_keys,
            "manus_deploy_github_url",
        )


BRANCH_REGISTRY: dict[ContractWorkBranch, BranchConfig] = {
    ContractWorkBranch.BASIC_LP: BranchConfig(
        refactor_key="basic_lp_refactored_source_markdown",
        canvas_key="basic_lp_manual_gemini_final",
        manual_meta_key="basic_lp_manual_gemini",
        extra_spec_keys=(
            "basic_lp_manual_gemini_step_4_wireframe",
            "basic_lp_manual_gemini_step_7_design_doc",
        ),
        use_gemini_flag="BASIC_LP_USE_GEMINI_MANUAL",
        refactor_flag="BASIC_LP_REFACTOR_AFTER_MANUAL",
        plan_label="BASIC LP TEXT_LLM",
        pipeline_module="modules.basic_lp_gemini_manual",
        pipeline_function="run_basic_lp_gemini_manual_pipeline",
    ),
    ContractWorkBranch.BASIC: BranchConfig(
        refactor_key="basic_refactored_source_markdown",
        canvas_key="basic_manual_gemini_final",
        manual_meta_key="basic_cp_manual_gemini",
        extra_spec_keys=(
            "basic_manual_gemini_step_2_structure",
            "basic_manual_gemini_step_6_design_doc",
        ),
        use_gemini_flag="BASIC_CP_USE_GEMINI_MANUAL",
        refactor_flag="BASIC_CP_REFACTOR_AFTER_MANUAL",
        plan_label="BASIC TEXT_LLM",
        pipeline_module="modules.basic_cp_gemini_manual",
        pipeline_function="run_basic_cp_gemini_manual_pipeline",
    ),
    ContractWorkBranch.STANDARD: BranchConfig(
        refactor_key="standard_refactored_source_markdown",
        canvas_key="standard_manual_gemini_final",
        manual_meta_key="standard_cp_manual_gemini",
        extra_spec_keys=(
            "standard_manual_gemini_step_2",
            "standard_manual_gemini_step_6",
        ),
        use_gemini_flag="STANDARD_CP_USE_GEMINI_MANUAL",
        refactor_flag="STANDARD_CP_REFACTOR_AFTER_MANUAL",
        plan_label="STANDARD TEXT_LLM",
        pipeline_module="modules.standard_cp_gemini_manual",
        pipeline_function="run_standard_cp_gemini_manual_pipeline",
    ),
    ContractWorkBranch.ADVANCE: BranchConfig(
        refactor_key="advance_refactored_source_markdown",
        canvas_key="advance_manual_gemini_final",
        manual_meta_key="advance_cp_manual_gemini",
        extra_spec_keys=(
            "advance_manual_gemini_step_2",
            "advance_manual_gemini_step_6",
        ),
        use_gemini_flag="ADVANCE_CP_USE_GEMINI_MANUAL",
        refactor_flag="ADVANCE_CP_REFACTOR_AFTER_MANUAL",
        plan_label="ADVANCE TEXT_LLM",
        pipeline_module="modules.advance_cp_gemini_manual",
        pipeline_function="run_advance_cp_gemini_manual_pipeline",
    ),
}


def resolve_contract_work_branch(contract_plan: str) -> ContractWorkBranch:
    """
    契約プラン列の値から作業分岐を解決する。

    シート上の表記ゆれ（大文字小文字など）は ``get_contract_plan_info`` に合わせて正規化される。
    未定義のプラン名は STANDARD 相当の情報にフォールバックしたうえで ``STANDARD`` 分岐となる。
    """
    info = get_contract_plan_info((contract_plan or "").strip())
    name = (info.get("name") or "").strip().upper()
    pages = int(info.get("pages") or 1)
    if info.get("type") == "landing_page" or name == "BASIC LP":
        return ContractWorkBranch.BASIC_LP
    if name == "BASIC" and pages == 1:
        return ContractWorkBranch.BASIC
    if name == "ADVANCE":
        return ContractWorkBranch.ADVANCE
    if name == "STANDARD":
        return ContractWorkBranch.STANDARD
    return ContractWorkBranch.STANDARD


def resolve_work_branch_with_basic_lp_override(
    contract_plan: str,
    *,
    record_number: str,
    partner_name: str,
    lookup_basic_is_landing_page: Callable[[str, str], bool | None],
) -> ContractWorkBranch:
    """
    ``main.process_case`` と同じ最終作業分岐。

    契約プラン列から ``resolve_contract_work_branch`` したあと、分岐が BASIC のときだけ
    サイトタイプシート（B列=パートナー名・G列=``lp``/``cp_basic``）を参照する。
    ``lookup_basic_is_landing_page`` が ``True`` なら BASIC_LP、``False`` なら BASIC のまま、
    ``None`` なら上書きしない。
    """
    work_branch = resolve_contract_work_branch(contract_plan)
    if work_branch != ContractWorkBranch.BASIC:
        return work_branch
    lp_flag = lookup_basic_is_landing_page(record_number, partner_name)
    if lp_flag is True:
        return ContractWorkBranch.BASIC_LP
    return work_branch


def gemini_manual_enabled_for_branch(work_branch: ContractWorkBranch) -> bool:
    """該当プランで Gemini マニュアルチェーンが有効か（フェンス必須判定などに使用）。"""
    from config import config as cfg

    info = BRANCH_REGISTRY.get(work_branch)
    if info is None:
        return False
    return bool(getattr(cfg, info.use_gemini_flag, False))
