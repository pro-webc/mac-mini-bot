"""契約プラン列 → 作業分岐"""
from __future__ import annotations

import config.config as cfg
from modules.contract_workflow import (
    ContractWorkBranch,
    gemini_manual_enabled_for_branch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)


def test_branch_basic_lp() -> None:
    assert resolve_contract_work_branch("BASIC LP") == ContractWorkBranch.BASIC_LP
    assert resolve_contract_work_branch("basic lp") == ContractWorkBranch.BASIC_LP


def test_branch_basic() -> None:
    assert resolve_contract_work_branch("BASIC") == ContractWorkBranch.BASIC


def test_branch_standard() -> None:
    assert resolve_contract_work_branch("STANDARD") == ContractWorkBranch.STANDARD


def test_branch_standard_with_price_suffix_matches_sheet_style() -> None:
    """スプレッドシートである「STANDARD(14,800円)」表記はキー完全一致しないが STANDARD 情報にフォールバックする。"""
    assert resolve_contract_work_branch("STANDARD(14,800円)") == ContractWorkBranch.STANDARD


def test_branch_advance() -> None:
    assert resolve_contract_work_branch("ADVANCE") == ContractWorkBranch.ADVANCE


def test_unknown_plan_falls_back_to_standard_branch() -> None:
    assert resolve_contract_work_branch("NO_SUCH_PLAN_XYZ") == ContractWorkBranch.STANDARD


def test_resolve_work_branch_basic_lp_override_true() -> None:
    def lookup(_r: str, _p: str) -> bool | None:
        return True

    b = resolve_work_branch_with_basic_lp_override(
        "BASIC",
        record_number="1",
        partner_name="テスト社",
        lookup_basic_is_landing_page=lookup,
    )
    assert b == ContractWorkBranch.BASIC_LP


def test_resolve_work_branch_basic_lp_override_false() -> None:
    def lookup(_r: str, _p: str) -> bool | None:
        return False

    b = resolve_work_branch_with_basic_lp_override(
        "BASIC",
        record_number="1",
        partner_name="テスト社",
        lookup_basic_is_landing_page=lookup,
    )
    assert b == ContractWorkBranch.BASIC


def test_resolve_work_branch_basic_lp_override_none_stays_basic() -> None:
    def lookup(_r: str, _p: str) -> bool | None:
        return None

    b = resolve_work_branch_with_basic_lp_override(
        "BASIC",
        record_number="1",
        partner_name="テスト社",
        lookup_basic_is_landing_page=lookup,
    )
    assert b == ContractWorkBranch.BASIC


def test_resolve_work_branch_non_basic_skips_lookup() -> None:
    called = 0

    def lookup(_r: str, _p: str) -> bool | None:
        nonlocal called
        called += 1
        return True

    b = resolve_work_branch_with_basic_lp_override(
        "STANDARD",
        record_number="1",
        partner_name="テスト社",
        lookup_basic_is_landing_page=lookup,
    )
    assert b == ContractWorkBranch.STANDARD
    assert called == 0


def test_resolve_work_branch_basic_lp_never_calls_lookup() -> None:
    def boom(_r: str, _p: str) -> bool | None:
        raise AssertionError("BASIC LP は別シート参照しない")

    b = resolve_work_branch_with_basic_lp_override(
        "BASIC LP",
        record_number="1",
        partner_name="テスト社",
        lookup_basic_is_landing_page=boom,
    )
    assert b == ContractWorkBranch.BASIC_LP


def test_gemini_manual_enabled_for_branch(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "BASIC_LP_USE_GEMINI_MANUAL", True)
    monkeypatch.setattr(cfg, "BASIC_CP_USE_GEMINI_MANUAL", False)
    assert gemini_manual_enabled_for_branch(ContractWorkBranch.BASIC_LP) is True
    assert gemini_manual_enabled_for_branch(ContractWorkBranch.BASIC) is False
