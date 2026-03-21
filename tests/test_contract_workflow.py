"""契約プラン列 → 作業分岐"""
from modules.contract_workflow import ContractWorkBranch, resolve_contract_work_branch


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
