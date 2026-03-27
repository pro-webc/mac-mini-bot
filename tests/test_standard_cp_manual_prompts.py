"""STANDARD-CP マニュアルプロンプトの存在とプレースホルダ置換"""
from pathlib import Path

import pytest
from modules.standard_cp_claude_manual import (
    _standard_cp_tab4_history_from_user_model_pairs,
    _subst,
    _tab4_chat_history_after_step_3_1,
    _tab4_chat_history_after_step_3_2,
    _tab4_chat_history_after_step_3_3,
    _tab4_chat_history_after_step_3_4,
    build_standard_cp_claude_prompt_step_1_2,
    build_standard_cp_claude_prompt_step_1_2_and_1_3,
    build_standard_cp_claude_prompt_step_2,
    build_standard_cp_claude_prompt_step_3_1,
    build_standard_cp_claude_prompt_step_3_2,
    build_standard_cp_claude_prompt_step_3_3,
    build_standard_cp_claude_prompt_step_3_4,
    build_standard_cp_claude_prompt_step_3_5,
    build_standard_cp_claude_prompt_step_4,
    build_standard_cp_claude_prompt_step_5,
    build_standard_cp_claude_prompt_step_6,
    build_standard_cp_claude_prompt_step_7_1,
)

_MANUAL = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "prompts"
    / "standard_cp_manual"
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
    "step_7_5.txt",
)


@pytest.mark.parametrize("name", _EXPECTED_FILES)
def test_standard_cp_manual_prompt_file_exists(name: str) -> None:
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


def test_step_2_include_blog_true() -> None:
    out = build_standard_cp_claude_prompt_step_2(
        step_1_3_output="info", include_blog=True,
    )
    assert "・ブログページは必ず独立1ページ" in out


def test_step_2_include_blog_false() -> None:
    out = build_standard_cp_claude_prompt_step_2(
        step_1_3_output="info", include_blog=False,
    )
    assert "・ブログページは必ず独立1ページ" not in out


def test_build_standard_cp_claude_prompt_step_2_matches_subst() -> None:
    out = build_standard_cp_claude_prompt_step_2(step_1_3_output="手順13出力")
    assert "{{" not in out
    assert "手順13出力" in out


def test_build_standard_cp_claude_prompt_step_3_1_matches_subst() -> None:
    out = build_standard_cp_claude_prompt_step_3_1(
        step_2_output="構成案本文",
        step_1_3_output="お客様情報本文",
    )
    assert "{{" not in out
    assert "構成案本文" in out
    assert "お客様情報本文" in out
    assert "ヒアリング原文の再掲なし" in out


def test_build_standard_cp_claude_prompt_step_3_1_hearing_block() -> None:
    out = build_standard_cp_claude_prompt_step_3_1(
        step_2_output="構成",
        step_1_3_output="顧客",
        hearing_sheet_content="電話\n090-0000-0000\n",
    )
    assert "{{" not in out
    assert "090-0000-0000" in out


def test_build_standard_cp_claude_prompt_step_3_2_no_placeholders() -> None:
    out = build_standard_cp_claude_prompt_step_3_2()
    assert "{{" not in out
    assert "【手順.3-2】" in out


def test_build_standard_cp_claude_prompt_step_3_3_no_placeholders() -> None:
    out = build_standard_cp_claude_prompt_step_3_3()
    assert "{{" not in out
    assert "【手順.3-3】" in out


def test_build_standard_cp_claude_prompt_step_3_4_no_placeholders() -> None:
    out = build_standard_cp_claude_prompt_step_3_4()
    assert "{{" not in out
    assert "【手順.3-4】" in out


def test_build_standard_cp_claude_prompt_step_3_5_no_placeholders() -> None:
    out = build_standard_cp_claude_prompt_step_3_5()
    assert "{{" not in out
    assert "【手順.3-5】" in out


def test_build_standard_cp_claude_prompt_step_4_substitutes() -> None:
    out = build_standard_cp_claude_prompt_step_4(
        hearing_sheet_content="参考 https://example.com/design",
    )
    assert "{{" not in out
    assert "https://example.com/design" in out
    assert "HPに使いたい色" in out


def test_build_standard_cp_claude_prompt_step_5_substitutes() -> None:
    out = build_standard_cp_claude_prompt_step_5(
        step_4_output="手順4デザイン3点ブロック",
        step_1_3_output="お客様情報ブロック",
        step_2_output="サイト構成ブロック",
    )
    assert "{{" not in out
    assert "手順4デザイン3点ブロック" in out
    assert "お客様情報ブロック" in out
    assert "サイト構成ブロック" in out


def test_build_standard_cp_claude_prompt_step_6_substitutes() -> None:
    out = build_standard_cp_claude_prompt_step_6(
        hearing_sheet_content="参考サイトは https://a.example.com です。デザインはシンプル希望。",
    )
    assert "{{" not in out
    assert "【手順6】" in out
    assert "参考サイト" in out or "https://a.example.com" in out


def test_build_standard_cp_claude_prompt_step_7_1_substitutes() -> None:
    out = build_standard_cp_claude_prompt_step_7_1(
        step_6_output="# デザイン生成指示書\n…",
        hearing_sheet_content="配色はブルー系希望",
    )
    assert "{{" not in out
    assert "# デザイン生成指示書" in out
    assert "配色" in out


def test_tab4_chat_history_after_step_3_1_shape() -> None:
    h = _tab4_chat_history_after_step_3_1(
        step_3_1_prompt="質問本文",
        step_3_1_response="回答本文",
    )
    assert len(h) == 2
    assert h[0] == {"role": "user", "content": "質問本文"}
    assert h[1] == {"role": "assistant", "content": "回答本文"}


def test_tab4_chat_history_after_step_3_2_shape() -> None:
    h = _tab4_chat_history_after_step_3_2(
        step_3_1_prompt="一問目",
        step_3_1_response="一答",
        step_3_2_prompt="二問目",
        step_3_2_response="二答",
    )
    assert len(h) == 4
    assert h[0]["role"] == "user" and h[1]["role"] == "assistant"
    assert h[2]["role"] == "user" and h[3]["role"] == "assistant"
    assert h[2] == {"role": "user", "content": "二問目"}


def test_tab4_chat_history_after_step_3_3_shape() -> None:
    h = _tab4_chat_history_after_step_3_3(
        step_3_1_prompt="a1",
        step_3_1_response="b1",
        step_3_2_prompt="a2",
        step_3_2_response="b2",
        step_3_3_prompt="a3",
        step_3_3_response="b3",
    )
    assert len(h) == 6
    assert h[-2] == {"role": "user", "content": "a3"}
    assert h[-1] == {"role": "assistant", "content": "b3"}


def test_tab4_chat_history_after_step_3_4_shape() -> None:
    h = _tab4_chat_history_after_step_3_4(
        step_3_1_prompt="a1",
        step_3_1_response="b1",
        step_3_2_prompt="a2",
        step_3_2_response="b2",
        step_3_3_prompt="a3",
        step_3_3_response="b3",
        step_3_4_prompt="a4",
        step_3_4_response="b4",
    )
    assert len(h) == 8
    assert h[-2] == {"role": "user", "content": "a4"}
    assert h[-1] == {"role": "assistant", "content": "b4"}


def test_standard_cp_tab4_history_rejects_empty_pairs() -> None:
    with pytest.raises(RuntimeError, match="組が空"):
        _standard_cp_tab4_history_from_user_model_pairs([])


def test_tab4_chat_history_rejects_empty() -> None:
    with pytest.raises(RuntimeError, match="1 通目の user プロンプトが空"):
        _tab4_chat_history_after_step_3_1(
            step_3_1_prompt="",
            step_3_1_response="x",
        )
    with pytest.raises(RuntimeError, match="1 通目の assistant 応答が空"):
        _tab4_chat_history_after_step_3_1(
            step_3_1_prompt="x",
            step_3_1_response="",
        )
    with pytest.raises(RuntimeError, match="2 通目の user プロンプトが空"):
        _tab4_chat_history_after_step_3_2(
            step_3_1_prompt="a",
            step_3_1_response="b",
            step_3_2_prompt="",
            step_3_2_response="c",
        )
    with pytest.raises(RuntimeError, match="3 通目の user プロンプトが空"):
        _tab4_chat_history_after_step_3_3(
            step_3_1_prompt="a",
            step_3_1_response="b",
            step_3_2_prompt="c",
            step_3_2_response="d",
            step_3_3_prompt="",
            step_3_3_response="e",
        )
    with pytest.raises(RuntimeError, match="4 通目の user プロンプトが空"):
        _tab4_chat_history_after_step_3_4(
            step_3_1_prompt="a",
            step_3_1_response="b",
            step_3_2_prompt="c",
            step_3_2_response="d",
            step_3_3_prompt="e",
            step_3_3_response="f",
            step_3_4_prompt="",
            step_3_4_response="g",
        )


def test_step_1_2_prompt_builder_substitutes_all_placeholders() -> None:
    out = build_standard_cp_claude_prompt_step_1_2(
        hearing_sheet_content="ヒアリング本文\n参考 https://example.com/ref",
        appo_memo="メモ",
        sales_notes="",
        existing_site_url="",
        step_1_1_output="手順1-1の応答",
    )
    assert "{{" not in out
    assert "手順1-1の応答" in out
    assert "メモ" in out


def test_step_1_2_and_1_3_combined_joins_both_sections() -> None:
    out = build_standard_cp_claude_prompt_step_1_2_and_1_3(
        hearing_sheet_content="ヒアリング本文",
        appo_memo="アポ",
        sales_notes="",
        existing_site_url="",
        step_1_1_output="out1",
    )
    assert "{{" not in out
    assert "【手順.1-2】" in out
    assert "【手順.1-3】" in out
    assert "【会社概要" in out
    assert "out1" in out


def test_step_7_3_batch1_placeholder() -> None:
    t = _MANUAL.joinpath("step_7_3.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        STEP_3_LOWER_BATCH1="下層1群目",
        HEARING_FACTUAL_BLOCK="事実抜粋",
    )
    assert "{{" not in out
    assert "下層1群目" in out
    assert "事実抜粋" in out


def test_step_7_4_batch2_placeholder() -> None:
    t = _MANUAL.joinpath("step_7_4.txt").read_text(encoding="utf-8")
    out = _subst(
        t,
        STEP_3_LOWER_BATCH2="下層2群目",
        HEARING_FACTUAL_BLOCK="事実抜粋2",
    )
    assert "{{" not in out
    assert "下層2群目" in out
    assert "事実抜粋2" in out


def test_step_7_5_no_placeholders() -> None:
    t = _MANUAL.joinpath("step_7_5.txt").read_text(encoding="utf-8")
    assert "{{" not in t
    assert "【手順.7-5】" in t
