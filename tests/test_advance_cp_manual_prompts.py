"""ADVANCE-CP マニュアルプロンプトの存在とプレースホルダ置換"""
from pathlib import Path

import pytest
from modules.advance_cp_claude_manual import _subst

_MANUAL = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "prompts"
    / "advance_cp_manual"
)

_EXPECTED_FILES = (
    "step_1_1.txt",
    "step_1_2.txt",
    "step_1_3.txt",
    "step_2.txt",
    "step_3_1.txt",
    "step_3_2.txt",
    "step_3_3.txt",
    "step_3_4.txt",
    "step_3_5.txt",
    "step_4.txt",
    "step_5.txt",
    "step_6.txt",
    "step_7_1.txt",
    "step_7_2.txt",
    "step_7_3.txt",
    "step_7_4.txt",
)


@pytest.mark.parametrize("name", _EXPECTED_FILES)
def test_advance_cp_manual_prompt_file_exists(name: str) -> None:
    assert (_MANUAL / name).is_file(), f"missing {name}"


def test_step_2_blog_placeholder() -> None:
    t = _MANUAL.joinpath("step_2.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        STEP_1_3_OUTPUT="顧客情報",
        BLOG_PAGE_LINE="・ブログ行\n",
    )
    assert "{{" not in out
    assert "顧客情報" in out
    assert "・ブログ行" in out
    assert "12ページ" in out


def test_step_7_3_batch1_placeholder() -> None:
    t = _MANUAL.joinpath("step_7_3.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        STEP_3_LOWER_BATCH1="下層1群",
        HEARING_FACTUAL_BLOCK="事実",
    )
    assert "{{" not in out
    assert "下層1群" in out


def test_step_7_4_batch2_placeholder() -> None:
    t = _MANUAL.joinpath("step_7_4.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        STEP_3_LOWER_BATCH2="下層2群",
        HEARING_FACTUAL_BLOCK="事実",
    )
    assert "{{" not in out
    assert "下層2群" in out
