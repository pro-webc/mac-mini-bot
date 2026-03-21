"""BASIC LP / BASIC-CP リファクタ用プロンプト"""
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
    assert "ソース" in p
    assert "リファクタ指示書" in p
    assert "BASIC LP" in p
    assert "preface_shared" not in p  # ファイル名はプロンプトに出さない
    assert "nanobanana" in p.lower()
    assert "同一のリファクタ指示書" in p
    assert "STANDARD-CP" in p
    assert "ADVANCE-CP" in p


def test_refactor_prompt_empty_raises() -> None:
    with pytest.raises(RuntimeError, match="空"):
        build_basic_lp_refactor_user_prompt("  \n  ")


def test_cp_refactor_preface_option() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "export default function Page() { return null }",
        preface_dir=BASIC_CP_REFACTOR_PREFACE_DIR,
    )
    assert "BASIC-CP" in p
    assert "===== BEGIN_CANVAS_SOURCE =====" in p


def test_standard_cp_refactor_preface_option() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "export default function App() { return null }",
        preface_dir=STANDARD_CP_REFACTOR_PREFACE_DIR,
    )
    assert "STANDARD-CP" in p
    assert "===== BEGIN_CANVAS_SOURCE =====" in p


def test_advance_cp_refactor_preface_option() -> None:
    p = build_basic_lp_refactor_user_prompt(
        "export default function App() { return null }",
        preface_dir=ADVANCE_CP_REFACTOR_PREFACE_DIR,
    )
    assert "ADVANCE-CP" in p
    assert "12ページ" in p
    assert "===== BEGIN_CANVAS_SOURCE =====" in p
