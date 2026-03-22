"""Manus リファクタ用プロンプト（手作業マニュアル同様の manus/*.txt）"""
import pytest
from modules.basic_lp_refactor_gemini import (
    ADVANCE_CP_REFACTOR_PREFACE_DIR,
    BASIC_CP_REFACTOR_PREFACE_DIR,
    STANDARD_CP_REFACTOR_PREFACE_DIR,
    build_basic_lp_refactor_user_prompt,
)


def test_refactor_prompt_contains_markers() -> None:
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


def test_refactor_prompt_partner_name_in_orchestration() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "export default function X() { return null }",
        partner_name="テスト商事",
    )
    assert "テスト商事" in p
    assert "{{PARTNER_NAME}}" not in p


def test_refactor_prompt_empty_raises() -> None:
    with pytest.raises(RuntimeError, match="空"):
        build_basic_lp_refactor_user_prompt("  \n  ")


def test_cp_preface_dir_ignored_same_as_handwork() -> None:
    """preface_dir は Manus 手作業プロンプトでは使わない（どの分岐も同一本文）。"""
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
