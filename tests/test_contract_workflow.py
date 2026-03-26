"""契約プラン列 → 作業分岐"""
from __future__ import annotations

import pytest

import config.config as cfg
from config.config import _normalize_plan_name
from modules.contract_workflow import (
    ContractWorkBranch,
    claude_manual_enabled_for_branch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("BASIC", "BASIC"),
        ("basic", "BASIC"),
        ("BASIC(9,800円)", "BASIC"),
        ("BASIC LP", "BASIC LP"),
        ("BASIC  LP", "BASIC LP"),
        ("BASIC LP(9,800円)", "BASIC LP"),
        ("STANDARD(14,800円)", "STANDARD"),
        ("ADVANCE(29,800円)", "ADVANCE"),
        ("  BASIC  ", "BASIC"),
        ("", ""),
    ],
)
def test_normalize_plan_name(raw: str, expected: str) -> None:
    assert _normalize_plan_name(raw) == expected


def test_branch_basic_lp() -> None:
    assert resolve_contract_work_branch("BASIC LP") == ContractWorkBranch.BASIC_LP
    assert resolve_contract_work_branch("basic lp") == ContractWorkBranch.BASIC_LP


def test_branch_basic() -> None:
    assert resolve_contract_work_branch("BASIC") == ContractWorkBranch.BASIC


def test_branch_standard() -> None:
    assert resolve_contract_work_branch("STANDARD") == ContractWorkBranch.STANDARD


def test_branch_standard_with_price_suffix() -> None:
    """スプレッドシートの「STANDARD(14,800円)」表記でも STANDARD に解決される。"""
    assert resolve_contract_work_branch("STANDARD(14,800円)") == ContractWorkBranch.STANDARD


def test_branch_basic_with_price_suffix() -> None:
    """「BASIC(9,800円)」表記でも BASIC に解決される（旧実装では STANDARD フォールバックだった）。"""
    assert resolve_contract_work_branch("BASIC(9,800円)") == ContractWorkBranch.BASIC


def test_branch_advance_with_price_suffix() -> None:
    """「ADVANCE(29,800円)」表記でも ADVANCE に解決される。"""
    assert resolve_contract_work_branch("ADVANCE(29,800円)") == ContractWorkBranch.ADVANCE


def test_branch_basic_lp_with_price_suffix() -> None:
    """「BASIC LP(9,800円)」表記でも BASIC_LP に解決される。"""
    assert resolve_contract_work_branch("BASIC LP(9,800円)") == ContractWorkBranch.BASIC_LP


def test_branch_basic_lp_no_space_or_hyphen() -> None:
    """スペース無し・ハイフン表記でも BASIC LP プランとして解決される。"""
    assert resolve_contract_work_branch("BASICLP") == ContractWorkBranch.BASIC_LP
    assert resolve_contract_work_branch("basic-lp") == ContractWorkBranch.BASIC_LP


def test_get_contract_plan_info_matches_longest_plan_key_first() -> None:
    """BASIC LP が BASIC より優先してマッチする（キー長ソートの退行防止）。"""
    from config.config import get_contract_plan_info

    lp = get_contract_plan_info("BASIC LP")
    assert lp["name"] == "BASIC LP"
    assert lp["type"] == "landing_page"
    basic = get_contract_plan_info("BASIC")
    assert basic["name"] == "BASIC"
    assert basic["type"] == "website"


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


def test_claude_manual_enabled_for_branch(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "BASIC_LP_USE_CLAUDE_MANUAL", True)
    monkeypatch.setattr(cfg, "BASIC_CP_USE_CLAUDE_MANUAL", False)
    assert claude_manual_enabled_for_branch(ContractWorkBranch.BASIC_LP) is True
    assert claude_manual_enabled_for_branch(ContractWorkBranch.BASIC) is False
