"""契約プラン列 → 作業分岐"""
import config.config as cfg

from modules.contract_workflow import (
    ContractWorkBranch,
    gemini_manual_enabled_for_branch,
    resolve_contract_work_branch,
)


def test_branch_basic_lp() -> None:
    assert resolve_contract_work_branch("BASIC LP") == ContractWorkBranch.BASIC_LP
    assert resolve_contract_work_branch("basic lp") == ContractWorkBranch.BASIC_LP


def test_branch_basic() -> None:
    assert resolve_contract_work_branch("BASIC") == ContractWorkBranch.BASIC


def test_branch_standard() -> None:
    assert resolve_contract_work_branch("STANDARD") == ContractWorkBranch.STANDARD


def test_branch_advance() -> None:
    assert resolve_contract_work_branch("ADVANCE") == ContractWorkBranch.ADVANCE


def test_unknown_plan_falls_back_to_standard_branch() -> None:
    assert resolve_contract_work_branch("NO_SUCH_PLAN_XYZ") == ContractWorkBranch.STANDARD


def test_gemini_manual_enabled_for_branch(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "BASIC_LP_USE_GEMINI_MANUAL", True)
    monkeypatch.setattr(cfg, "BASIC_CP_USE_GEMINI_MANUAL", False)
    assert gemini_manual_enabled_for_branch(ContractWorkBranch.BASIC_LP) is True
    assert gemini_manual_enabled_for_branch(ContractWorkBranch.BASIC) is False
