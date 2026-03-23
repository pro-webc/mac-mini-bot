"""Manus リファクタ用プロンプト（手作業マニュアル同様の manus/*.txt）"""
import modules.basic_lp_refactor_gemini as refactor_mod
import pytest
from modules.basic_lp_refactor_gemini import (
    ADVANCE_CP_REFACTOR_PREFACE_DIR,
    BASIC_CP_REFACTOR_PREFACE_DIR,
    STANDARD_CP_REFACTOR_PREFACE_DIR,
    build_basic_lp_refactor_user_prompt,
)


def test_refactor_prompt_contains_markers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", True)
    p = build_basic_lp_refactor_user_prompt("export default function X() { return null }")
    assert "===== BEGIN_CANVAS_SOURCE =====" in p
    assert "===== END_CANVAS_SOURCE =====" in p
    assert "export default function X()" in p
    assert "リファクタリング指示書" in p
    assert "propagate-webcreation" in p
    assert "DefaultSetting" in p
    assert "nanobanana" in p.lower()
    assert "public/images" in p.lower()
    assert "next/image" in p.lower()
    assert "BOT_DEPLOY_GITHUB_URL:" in p


def test_refactor_prompt_without_deploy_url_block_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", False)
    p = build_basic_lp_refactor_user_prompt("const x = 1")
    assert "BOT_DEPLOY_GITHUB_URL:" not in p


def test_refactor_prompt_deploy_hint_from_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", True)
    monkeypatch.setattr(refactor_mod, "MANUS_DEPLOY_GITHUB_REPO_HINT", "org/bot-99-acme")
    p = build_basic_lp_refactor_user_prompt("const x = 1")
    assert "org/bot-99-acme" in p
    assert "https://github.com/org/bot-99-acme.git" in p


def test_refactor_prompt_repo_name_and_description_in_orchestration() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "export default function X() { return null }",
        partner_name="テスト商事",
        record_number="",
    )
    assert "test-run-0" in p
    assert "テスト商事" in p
    assert "{{MANUS_REPO_NAME}}" not in p
    assert "{{MANUS_REPO_DESCRIPTION}}" not in p


def test_refactor_prompt_record_number_in_repo_name() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "const x = 1",
        partner_name="ACME株式会社",
        record_number="12345",
    )
    assert "test-run-12345" in p
    assert "ACME株式会社" in p


def test_refactor_prompt_empty_raises() -> None:
    with pytest.raises(RuntimeError, match="空"):
        build_basic_lp_refactor_user_prompt("  \n  ")


def test_cp_preface_dir_ignored_same_as_handwork(monkeypatch: pytest.MonkeyPatch) -> None:
    """preface_dir は Manus 手作業プロンプトでは使わない（どの分岐も同一本文）。"""
    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", False)
    base = build_basic_lp_refactor_user_prompt("const x = 1")
    p_cp = build_basic_lp_refactor_user_prompt(
        "const x = 1",
        preface_dir=BASIC_CP_REFACTOR_PREFACE_DIR,
    )
    p_st = build_basic_lp_refactor_user_prompt(
        "const x = 1",
        preface_dir=STANDARD_CP_REFACTOR_PREFACE_DIR,
    )
    p_adv = build_basic_lp_refactor_user_prompt(
        "const x = 1",
        preface_dir=ADVANCE_CP_REFACTOR_PREFACE_DIR,
    )
    assert base == p_cp == p_st == p_adv
