"""BASIC-CP マニュアルプロンプトファイルの存在とプレースホルダ置換"""
from pathlib import Path

import pytest
from modules.basic_cp_gemini_manual import _subst

_MANUAL = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "prompts"
    / "basic_cp_manual"
)

_EXPECTED_FILES = (
    "step_1_1.txt",
    "step_1_2.txt",
    "step_1_3.txt",
    "step_2.txt",
    "step_3.txt",
    "step_4.txt",
    "step_5.txt",
    "step_6.txt",
    "step_7_1.txt",
    "step_7_2.txt",
    "step_7_3.txt",
)


@pytest.mark.parametrize("name", _EXPECTED_FILES)
def test_basic_cp_manual_prompt_file_exists(name: str) -> None:
    assert (_MANUAL / name).is_file(), f"missing {name}"


def test_subst_fills_step_1_1_placeholder() -> None:
    t = _MANUAL.joinpath("step_1_1.txt").read_text(encoding="utf-8")
    out = _subst(t, HEARING_BLOCK="Q: テスト\nA: 回答")
    assert "{{" not in out
    assert "Q: テスト" in out


def test_subst_step_7_2_fills_step_3() -> None:
    t = _MANUAL.joinpath("step_7_2.txt").read_text(encoding="utf-8")
    out = _subst(t, STEP_3_OUTPUT="構成本文")
    assert "{{" not in out
    assert "構成本文" in out


def test_subst_rejects_unfilled_placeholder() -> None:
    with pytest.raises(RuntimeError, match="未置換"):
        _subst("a {{X}} b", Y="1")
