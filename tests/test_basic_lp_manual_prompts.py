"""BASIC LP マニュアルプロンプトファイルの存在とプレースホルダ置換"""
from pathlib import Path

import pytest
from modules.basic_lp_claude_manual import _subst

_MANUAL = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "prompts"
    / "basic_lp_manual"
)

_EXPECTED_FILES = (
    "step_1_1.txt",
    "step_1_2.txt",
    "step_1_3_nonrecruit.txt",
    "step_2.txt",
    "step_3.txt",
    "step_4.txt",
    "step_5.txt",
    "step_6.txt",
    "step_7.txt",
    "step_8_1.txt",
    "step_8_2.txt",
    "step_8_3.txt",
)


@pytest.mark.parametrize("name", _EXPECTED_FILES)
def test_basic_lp_manual_prompt_file_exists(name: str) -> None:
    assert (_MANUAL / name).is_file(), f"missing {name}"


def test_subst_fills_step_1_1_placeholder() -> None:
    t = _MANUAL.joinpath("step_1_1.txt").read_text(encoding="utf-8")
    out = _subst(t, HEARING_BLOCK="Q: テスト\nA: 回答")
    assert "{{" not in out
    assert "Q: テスト" in out


def test_subst_rejects_unfilled_placeholder() -> None:
    with pytest.raises(RuntimeError, match="未置換"):
        _subst("a {{X}} b", Y="1")


def test_subst_step_8_1_fills_design_and_wire_placeholders() -> None:
    t = _MANUAL.joinpath("step_8_1.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        HEARING_REFERENCE_DESIGN_BLOCK="（テスト用再掲）参考サイトの雰囲気",
        STEP_7_OUTPUT="デザイン指示書本文",
        STEP_4_OUTPUT="手順4ワイヤー原稿本文",
    )
    assert "{{" not in out
    assert "デザイン指示書本文" in out
    assert "手順4ワイヤー原稿本文" in out


def test_subst_step_6_fills_design_and_structure_placeholders() -> None:
    t = _MANUAL.joinpath("step_6.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        HEARING_REFERENCE_DESIGN_BLOCK="（テスト用再掲）デザイン希望",
        HEARING_1_3_OUTPUT="ヒアリング本文",
        STEP_4_OUTPUT="ワイヤー構成本文",
        STEP_5_OUTPUT="手順5デザイン3点本文",
    )
    assert "{{" not in out
    assert "ヒアリング本文" in out
    assert "ワイヤー構成本文" in out
    assert "手順5デザイン3点本文" in out
