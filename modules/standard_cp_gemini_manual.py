"""STANDARD-CP（コーポレート・6ページ想定）制作マニュアルに沿った Gemini 多段チェーン。

**API 呼び出し回数（マニュアルの「新規チャット」「タブ」境界と一致）**

- 合計 **15 回**（各回が ``generate_content`` または ``send_message`` の1回）
- **新規チャット** はマニュアルの **タブ①〜⑥** に対応し **6 回**

内訳（1 + 1 + 1 + 5 + 3 + 4 = 15）:

- **タブ①**: 手順1-1 → 1回
- **タブ②**: 手順1-2 と 手順1-3 を **1メッセージに連結**して送信 → 1回（手作業マニュアルと同じ）
- **タブ③**: 手順2（6ページ構成）→ 1回
- **タブ④**: 手順3-1 → … → 3-5 → 5回（ページ別・同一チャット）
- **タブ⑤**: 手順4 → 5 → 6 → 3回（配色・デザイン指示書）
- **タブ⑥**: 手順7-1 → 7-2 → 7-3 → 7-4 → 4回（コード・Canvas 想定）

**手順7の「複数タブで試す」** は人手任意。本モジュールは **タブ⑥を1本分**のみ（7-1〜7-4 の4回）。

**リファクタ**（任意・既定オン）: ``STANDARD_CP_REFACTOR_AFTER_MANUAL`` で **Manus タスク1件**。
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import google.generativeai as genai
from config.config import (
    GEMINI_STANDARD_CP_MODEL,
    STANDARD_CP_INCLUDE_BLOG_PAGE,
    STANDARD_CP_REFACTOR_AFTER_MANUAL,
    STANDARD_CP_USE_GEMINI_MANUAL,
    get_contract_plan_info,
)

from modules.basic_lp_refactor_gemini import (
    BASIC_LP_REFACTOR_MANUS_TASKS,
    STANDARD_CP_REFACTOR_PREFACE_DIR,
)
from modules.contract_workflow import ContractWorkBranch
from modules.hearing_url_utils import (
    hearing_factual_data_block_for_prompt,
    hearing_reference_design_block_for_prompt,
)
from modules.llm.llm_pipeline_common import MIN_SITE_BUILD_PROMPT_CHARS, finalize_plain_prompt

logger = logging.getLogger(__name__)

STANDARD_CP_MANUAL_GEMINI_API_CALLS_PER_CASE = 15
STANDARD_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS = 6

from modules.gemini_manual_common import (
    SAFETY_SETTINGS as _SAFETY,
    configure_gemini as _configure,
    gen_config as _gen_config,
    response_text as _response_text_impl,
    hearing_block as _hearing_block_impl,
    existing_site_url_block as _existing_site_url_block,
    client_hp_and_mood_placeholders as _client_hp_and_mood_placeholders,
    reference_url_block as _reference_url_block,
    load_step as _load_step_impl,
    subst as _subst_impl,
)

_MODULE_NAME = "modules.standard_cp_gemini_manual"
_MANUAL_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "standard_cp_manual"


def _load_step(filename: str) -> str:
    return _load_step_impl(_MANUAL_DIR, filename, module_name=_MODULE_NAME)


def _subst(template: str, **kwargs: str) -> str:
    return _subst_impl(template, module_name=_MODULE_NAME, **kwargs)


def _hearing_block(hearing_sheet_content: str) -> str:
    return _hearing_block_impl(hearing_sheet_content, module_name=_MODULE_NAME)


def _response_text(response: Any) -> str:
    return _response_text_impl(
        response, module_name=_MODULE_NAME, warn_max_tokens=True,
    )


def _blog_page_line() -> str:
    if STANDARD_CP_INCLUDE_BLOG_PAGE:
        return "・ブログページは必ず独立1ページ(不必要の場合は必ず削除)\n"
    return ""


def build_standard_cp_gemini_prompt_step_1_1(*, hearing_sheet_content: str) -> str:
    """手順1-1（タブ①・API 1/15）に渡すプロンプト全文。``generate_content`` は呼ばない。"""
    hear = _hearing_block(hearing_sheet_content)
    return _subst(_load_step("step_1_1.txt"), HEARING_BLOCK=hear)


def _appo_memo_block(appo_memo: str, sales_notes: str) -> str:
    ap_block = (appo_memo or "").strip()
    if (sales_notes or "").strip():
        ap_block += (
            "\n\n【営業メモ・その他先方情報】\n"
            + (sales_notes or "").strip()
        )
    return ap_block or "（なし）"


def build_standard_cp_gemini_prompt_step_1_2(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    existing_site_url: str = "",
    step_1_1_output: str,
) -> str:
    """手順1-2のみ（タブ②の前半）。タブ②送信時は ``build_standard_cp_gemini_prompt_step_1_2_and_1_3`` を使う。"""
    return _subst(
        _load_step("step_1_2.txt"),
        STEP_1_1_OUTPUT=step_1_1_output,
        APPO_MEMO=_appo_memo_block(appo_memo, sales_notes),
        EXISTING_SITE_URL_BLOCK=_existing_site_url_block(
            hearing_sheet_content, existing_site_url
        ),
    )


def build_standard_cp_gemini_prompt_step_1_2_and_1_3(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    existing_site_url: str = "",
    step_1_1_output: str,
) -> str:
    """
    手順1-2 と 手順1-3 を連結した1本（タブ②・1メッセージ）。

    マニュアル手作業では「先に読み込み（1-2）」と「項目埋め（1-3）」を **同一送信** にする。
    """
    p12 = build_standard_cp_gemini_prompt_step_1_2(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
        existing_site_url=existing_site_url,
        step_1_1_output=step_1_1_output,
    )
    p13 = _load_step("step_1_3.txt")
    return f"{p12.rstrip()}\n\n{p13.lstrip()}"


def build_standard_cp_gemini_prompt_step_2(*, step_1_3_output: str) -> str:
    """手順2（タブ③・API 3/15）に渡すプロンプト全文。``send_message`` は呼ばない。"""
    return _subst(
        _load_step("step_2.txt"),
        STEP_1_3_OUTPUT=step_1_3_output,
        BLOG_PAGE_LINE=_blog_page_line(),
    )


def build_standard_cp_gemini_prompt_step_3_1(
    *,
    step_2_output: str,
    step_1_3_output: str,
    hearing_sheet_content: str = "",
) -> str:
    """手順3-1（タブ④・API 4/15）に渡すプロンプト全文。``send_message`` は呼ばない。"""
    hear = (hearing_sheet_content or "").strip()
    block = (
        hear
        if hear
        else "（ヒアリング原文の再掲なし。以下お客様情報のみ参照すること。）"
    )
    return _subst(
        _load_step("step_3_1.txt"),
        STEP_2_OUTPUT=step_2_output,
        STEP_1_3_OUTPUT=step_1_3_output,
        HEARING_BLOCK=block,
    )


def build_standard_cp_gemini_prompt_step_3_2() -> str:
    """手順3-2（タブ④・API 5/15）に渡すプロンプト全文。置換なし。``send_message`` は呼ばない。"""
    return _load_step("step_3_2.txt")


def build_standard_cp_gemini_prompt_step_3_3() -> str:
    """手順3-3（タブ④・API 6/15）に渡すプロンプト全文。置換なし。``send_message`` は呼ばない。"""
    return _load_step("step_3_3.txt")


def build_standard_cp_gemini_prompt_step_3_4() -> str:
    """手順3-4（タブ④・API 7/15）に渡すプロンプト全文。置換なし。``send_message`` は呼ばない。"""
    return _load_step("step_3_4.txt")


def build_standard_cp_gemini_prompt_step_3_5() -> str:
    """手順3-5（タブ④・API 8/15）に渡すプロンプト全文。置換なし。``send_message`` は呼ばない。"""
    return _load_step("step_3_5.txt")


def build_standard_cp_gemini_prompt_step_4(
    *,
    hearing_sheet_content: str,
    appo_memo: str = "",
    sales_notes: str = "",
) -> str:
    """手順4（タブ⑤・API 9/15）に渡すプロンプト全文。``send_message`` は呼ばない。"""
    hp_c, mood_c = _client_hp_and_mood_placeholders()
    extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    return _subst(
        _load_step("step_4.txt"),
        HP_COLOR_CLIENT=hp_c,
        MOOD_CLIENT=mood_c,
        REFERENCE_URL_BLOCK=_reference_url_block(hearing_sheet_content, extra_texts=extras),
    )


def build_standard_cp_gemini_prompt_step_5(
    *,
    step_4_output: str,
    step_1_3_output: str,
    step_2_output: str,
) -> str:
    """手順5（タブ⑤・API 10/15）に渡すプロンプト全文。``send_message`` は呼ばない。"""
    return _subst(
        _load_step("step_5.txt"),
        STEP_4_OUTPUT=step_4_output,
        HEARING_1_3_OUTPUT=step_1_3_output,
        STEP_2_OUTPUT=step_2_output,
    )


def build_standard_cp_gemini_prompt_step_6(
    *,
    hearing_sheet_content: str,
    appo_memo: str = "",
    sales_notes: str = "",
) -> str:
    """手順6（タブ⑤・API 11/15）に渡すプロンプト全文。参考サイト・デザイン原文を再掲する。"""
    extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    return _subst(
        _load_step("step_6.txt"),
        HEARING_REFERENCE_DESIGN_BLOCK=hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=extras,
        ),
    )


def build_standard_cp_gemini_prompt_step_7_1(
    *,
    step_6_output: str,
    hearing_sheet_content: str,
    appo_memo: str = "",
    sales_notes: str = "",
) -> str:
    """手順7-1（タブ⑥・API 12/15）に渡すプロンプト全文。新規チャットのためヒアリング再掲あり。"""
    extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    return _subst(
        _load_step("step_7_1.txt"),
        STEP_6_OUTPUT=(step_6_output or "").strip(),
        HEARING_REFERENCE_DESIGN_BLOCK=hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=extras,
        ),
    )


def _standard_cp_tab4_history_from_user_model_pairs(
    pairs: Sequence[tuple[str, str]],
) -> list[dict[str, Any]]:
    """タブ④の ``start_chat(history=...)`` 用。各要素は (user プロンプト, model 応答) の1往復。"""
    if not pairs:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: タブ④履歴にする user/model の組が空です。"
        )
    hist: list[dict[str, Any]] = []
    for n, (u_raw, m_raw) in enumerate(pairs, start=1):
        u = (u_raw or "").strip()
        m = (m_raw or "").strip()
        if not u:
            raise RuntimeError(
                "modules.standard_cp_gemini_manual: タブ④履歴 "
                f"{n} 通目の user プロンプトが空です（段階テストの継続用）。"
            )
        if not m:
            raise RuntimeError(
                "modules.standard_cp_gemini_manual: タブ④履歴 "
                f"{n} 通目の model 応答が空です（段階テストの継続用）。"
            )
        hist.append({"role": "user", "parts": [u]})
        hist.append({"role": "model", "parts": [m]})
    return hist


def _tab4_chat_history_after_step_3_1(
    *, step_3_1_prompt: str, step_3_1_response: str
) -> list[dict[str, Any]]:
    """タブ④で手順3-1 まで終えたあとの ``start_chat(history=...)`` 用履歴（本番と同じ1往復）。"""
    return _standard_cp_tab4_history_from_user_model_pairs(
        [(step_3_1_prompt, step_3_1_response)]
    )


def _tab4_chat_history_after_step_3_2(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
) -> list[dict[str, Any]]:
    """タブ④で手順3-2 まで終えたあとの ``start_chat(history=...)`` 用履歴（本番と同じ2往復）。"""
    return _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_3_1_prompt, step_3_1_response),
            (step_3_2_prompt, step_3_2_response),
        ]
    )


def _tab4_chat_history_after_step_3_3(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
    step_3_3_prompt: str,
    step_3_3_response: str,
) -> list[dict[str, Any]]:
    """タブ④で手順3-3 まで終えたあとの ``start_chat(history=...)`` 用履歴（本番と同じ3往復）。"""
    return _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_3_1_prompt, step_3_1_response),
            (step_3_2_prompt, step_3_2_response),
            (step_3_3_prompt, step_3_3_response),
        ]
    )


def _tab4_chat_history_after_step_3_4(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
    step_3_3_prompt: str,
    step_3_3_response: str,
    step_3_4_prompt: str,
    step_3_4_response: str,
) -> list[dict[str, Any]]:
    """タブ④で手順3-4 まで終えたあとの ``start_chat(history=...)`` 用履歴（本番と同じ4往復）。"""
    return _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_3_1_prompt, step_3_1_response),
            (step_3_2_prompt, step_3_2_response),
            (step_3_3_prompt, step_3_3_response),
            (step_3_4_prompt, step_3_4_response),
        ]
    )


def run_standard_cp_gemini_api_call_1_of_15(
    *,
    hearing_sheet_content: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 1/15**（新規チャット・手順1-1）のみ。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_1_1(
        hearing_sheet_content=hearing_sheet_content
    )
    logger.info("STANDARD-CP Gemini: 手順1-1のみ（段階テスト・API 1/15）…")
    r11 = model.generate_content(prompt, generation_config=gcfg)
    return prompt, _response_text(r11)


def run_standard_cp_gemini_api_call_2_of_15(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    existing_site_url: str = "",
    step_1_1_output: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 2/15**（新規チャット・手順1-2+1-3 連結）。

    本番と同様 ``start_chat(history=[])`` のあと、**1-2 と 1-3 を連結したプロンプト**を
    ``send_message`` で1回だけ送る。

    Returns:
        (prompt_text, response_text) — 応答は従来の手順1-3相当（埋め済み項目）の1本
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_1_2_and_1_3(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
        existing_site_url=existing_site_url,
        step_1_1_output=step_1_1_output,
    )
    logger.info("STANDARD-CP Gemini: 手順1-2+1-3 連結（段階テスト・API 2/15）…")
    chat2 = model.start_chat(history=[])
    r12 = chat2.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r12)


def run_standard_cp_gemini_api_call_3_of_15(
    *,
    step_1_3_output: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 3/15**（新規チャット・手順2・タブ③）。

    本番と同様 ``start_chat(history=[])`` のあと ``send_message`` で1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_2(step_1_3_output=step_1_3_output)
    logger.info("STANDARD-CP Gemini: 手順2のみ（段階テスト・API 3/15）…")
    chat3 = model.start_chat(history=[])
    r2 = chat3.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r2)


def run_standard_cp_gemini_api_call_4_of_15(
    *,
    step_2_output: str,
    step_1_3_output: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 4/15**（新規チャット・手順3-1・タブ④の1通目）。

    本番と同様 ``start_chat(history=[])`` のあと ``send_message`` で1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_3_1(
        step_2_output=step_2_output,
        step_1_3_output=step_1_3_output,
        hearing_sheet_content="",
    )
    logger.info("STANDARD-CP Gemini: 手順3-1のみ（段階テスト・API 4/15）…")
    chat4 = model.start_chat(history=[])
    r31 = chat4.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r31)


def run_standard_cp_gemini_api_call_5_of_15(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 5/15**（タブ④の2通目・手順3-2）。

    本番と同様、手順3-1 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順3-2 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_3_2()
    hist = _tab4_chat_history_after_step_3_1(
        step_3_1_prompt=step_3_1_prompt,
        step_3_1_response=step_3_1_response,
    )
    logger.info("STANDARD-CP Gemini: 手順3-2のみ（段階テスト・API 5/15・タブ④継続）…")
    chat4 = model.start_chat(history=hist)
    r32 = chat4.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r32)


def run_standard_cp_gemini_api_call_6_of_15(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 6/15**（タブ④の3通目・手順3-3）。

    本番と同様、手順3-1〜3-2 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順3-3 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_3_3()
    hist = _tab4_chat_history_after_step_3_2(
        step_3_1_prompt=step_3_1_prompt,
        step_3_1_response=step_3_1_response,
        step_3_2_prompt=step_3_2_prompt,
        step_3_2_response=step_3_2_response,
    )
    logger.info("STANDARD-CP Gemini: 手順3-3のみ（段階テスト・API 6/15・タブ④継続）…")
    chat4 = model.start_chat(history=hist)
    r33 = chat4.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r33)


def run_standard_cp_gemini_api_call_7_of_15(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
    step_3_3_prompt: str,
    step_3_3_response: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 7/15**（タブ④の4通目・手順3-4）。

    本番と同様、手順3-1〜3-3 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順3-4 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_3_4()
    hist = _tab4_chat_history_after_step_3_3(
        step_3_1_prompt=step_3_1_prompt,
        step_3_1_response=step_3_1_response,
        step_3_2_prompt=step_3_2_prompt,
        step_3_2_response=step_3_2_response,
        step_3_3_prompt=step_3_3_prompt,
        step_3_3_response=step_3_3_response,
    )
    logger.info("STANDARD-CP Gemini: 手順3-4のみ（段階テスト・API 7/15・タブ④継続）…")
    chat4 = model.start_chat(history=hist)
    r34 = chat4.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r34)


def run_standard_cp_gemini_api_call_8_of_15(
    *,
    step_3_1_prompt: str,
    step_3_1_response: str,
    step_3_2_prompt: str,
    step_3_2_response: str,
    step_3_3_prompt: str,
    step_3_3_response: str,
    step_3_4_prompt: str,
    step_3_4_response: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 8/15**（タブ④の5通目・手順3-5）。

    本番と同様、手順3-1〜3-4 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順3-5 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_3_5()
    hist = _tab4_chat_history_after_step_3_4(
        step_3_1_prompt=step_3_1_prompt,
        step_3_1_response=step_3_1_response,
        step_3_2_prompt=step_3_2_prompt,
        step_3_2_response=step_3_2_response,
        step_3_3_prompt=step_3_3_prompt,
        step_3_3_response=step_3_3_response,
        step_3_4_prompt=step_3_4_prompt,
        step_3_4_response=step_3_4_response,
    )
    logger.info("STANDARD-CP Gemini: 手順3-5のみ（段階テスト・API 8/15・タブ④継続）…")
    chat4 = model.start_chat(history=hist)
    r35 = chat4.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r35)


def run_standard_cp_gemini_api_call_9_of_15(
    *,
    hearing_sheet_content: str,
    appo_memo: str = "",
    sales_notes: str = "",
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 9/15**（新規チャット・手順4・タブ⑤の1通目）。

    本番と同様 ``start_chat(history=[])`` のあと ``send_message`` で手順4 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_4(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    logger.info("STANDARD-CP Gemini: 手順4のみ（段階テスト・API 9/15・タブ⑤）…")
    chat5 = model.start_chat(history=[])
    r4 = chat5.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r4)


def run_standard_cp_gemini_api_call_10_of_15(
    *,
    step_4_prompt: str,
    step_4_response: str,
    step_1_3_output: str,
    step_2_output: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 10/15**（タブ⑤の2通目・手順5）。

    本番と同様、手順4 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順5 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_5(
        step_4_output=step_4_response,
        step_1_3_output=step_1_3_output,
        step_2_output=step_2_output,
    )
    hist = _standard_cp_tab4_history_from_user_model_pairs(
        [(step_4_prompt, step_4_response)]
    )
    logger.info("STANDARD-CP Gemini: 手順5のみ（段階テスト・API 10/15・タブ⑤継続）…")
    chat5 = model.start_chat(history=hist)
    r5 = chat5.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r5)


def run_standard_cp_gemini_api_call_11_of_15(
    *,
    step_4_prompt: str,
    step_4_response: str,
    step_5_prompt: str,
    step_5_response: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 11/15**（タブ⑤の3通目・手順6）。

    本番と同様、手順4〜5 の **同一チャット** を ``history`` で2往復復元したうえで
    ``send_message`` で手順6 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_6(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    hist = _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_4_prompt, step_4_response),
            (step_5_prompt, step_5_response),
        ]
    )
    logger.info("STANDARD-CP Gemini: 手順6のみ（段階テスト・API 11/15・タブ⑤継続）…")
    chat5 = model.start_chat(history=hist)
    r6 = chat5.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r6)


def run_standard_cp_gemini_api_call_12_of_15(
    *,
    step_6_output: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 12/15**（新規チャット・手順7-1・タブ⑥の1通目）。

    本番と同様 ``start_chat(history=[])`` のあと、手順6 の応答本文を ``STEP_6_OUTPUT`` に埋めた
    ``step_7_1.txt`` を ``send_message`` で1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = build_standard_cp_gemini_prompt_step_7_1(
        step_6_output=step_6_output,
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    logger.info("STANDARD-CP Gemini: 手順7-1のみ（段階テスト・API 12/15・タブ⑥）…")
    chat6 = model.start_chat(history=[])
    r71 = chat6.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r71)


def run_standard_cp_gemini_api_call_13_of_15(
    *,
    step_7_1_prompt: str,
    step_7_1_response: str,
    step_3_1_output: str,
    step_2_output: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 13/15**（タブ⑥の2通目・手順7-2）。

    本番と同様、手順7-1 までの **同一チャット** を ``history`` で復元したうえで
    ``send_message`` で手順7-2 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    _extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    _factual = hearing_factual_data_block_for_prompt(
        hearing_sheet_content, extra_texts=_extras,
    )
    prompt = _subst(
        _load_step("step_7_2.txt"),
        STEP_3_1_OUTPUT=(step_3_1_output or "").strip(),
        STEP_2_OUTPUT=(step_2_output or "").strip(),
        HEARING_FACTUAL_BLOCK=_factual,
    )
    hist = _standard_cp_tab4_history_from_user_model_pairs(
        [(step_7_1_prompt, step_7_1_response)]
    )
    logger.info("STANDARD-CP Gemini: 手順7-2のみ（段階テスト・API 13/15・タブ⑥継続）…")
    chat6 = model.start_chat(history=hist)
    r72 = chat6.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r72)


def run_standard_cp_gemini_api_call_14_of_15(
    *,
    step_7_1_prompt: str,
    step_7_1_response: str,
    step_7_2_prompt: str,
    step_7_2_response: str,
    step_3_subpages_output: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 14/15**（タブ⑥の3通目・手順7-3）。

    本番と同様、手順7-2 までの **同一チャット** を ``history`` で2往復復元したうえで
    ``send_message`` で手順7-3 を1回送る。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    _extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    _factual = hearing_factual_data_block_for_prompt(
        hearing_sheet_content, extra_texts=_extras,
    )
    prompt = _subst(
        _load_step("step_7_3.txt"),
        STEP_3_SUBPAGES_OUTPUT=(step_3_subpages_output or "").strip(),
        HEARING_FACTUAL_BLOCK=_factual,
    )
    hist = _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_7_1_prompt, step_7_1_response),
            (step_7_2_prompt, step_7_2_response),
        ]
    )
    logger.info("STANDARD-CP Gemini: 手順7-3のみ（段階テスト・API 14/15・タブ⑥継続）…")
    chat6 = model.start_chat(history=hist)
    r73 = chat6.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r73)


def run_standard_cp_gemini_api_call_15_of_15(
    *,
    step_7_1_prompt: str,
    step_7_1_response: str,
    step_7_2_prompt: str,
    step_7_2_response: str,
    step_7_3_prompt: str,
    step_7_3_response: str,
) -> tuple[str, str]:
    """
    STANDARD-CP マニュアル chain の **Gemini 15/15**（タブ⑥の4通目・手順7-4）。

    本番と同様、手順7-3 までの **同一チャット** を ``history`` で3往復復元したうえで
    ``send_message`` で手順7-4 を1回送る（テンプレにプレースホルダ無し）。

    Returns:
        (prompt_text, response_text)
    """
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    prompt = _load_step("step_7_4.txt")
    hist = _standard_cp_tab4_history_from_user_model_pairs(
        [
            (step_7_1_prompt, step_7_1_response),
            (step_7_2_prompt, step_7_2_response),
            (step_7_3_prompt, step_7_3_response),
        ]
    )
    logger.info("STANDARD-CP Gemini: 手順7-4のみ（段階テスト・API 15/15・タブ⑥継続）…")
    chat6 = model.start_chat(history=hist)
    r74 = chat6.send_message(prompt, generation_config=gcfg)
    return prompt, _response_text(r74)


@dataclass
class StandardCpManualGeminiOutputs:
    step_1_1: str = ""
    step_1_2_assistant_ack: str = ""
    step_1_3: str = ""
    step_2: str = ""
    step_3_1: str = ""
    step_3_2: str = ""
    step_3_3: str = ""
    step_3_4: str = ""
    step_3_5: str = ""
    step_4: str = ""
    step_5_assistant_ack: str = ""
    step_6: str = ""
    step_7_1: str = ""
    step_7_2: str = ""
    step_7_3: str = ""
    step_7_4: str = ""
    step_refactor: str = ""
    raw: dict[str, str] = field(default_factory=dict)
    raw_prompts: dict[str, str] = field(default_factory=dict)


def run_standard_cp_gemini_manual_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    record_number: str = "",
    existing_site_url: str = "",
) -> tuple[dict[str, Any], dict[str, Any], StandardCpManualGeminiOutputs]:
    if not STANDARD_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: STANDARD_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _manus_tasks = (
        BASIC_LP_REFACTOR_MANUS_TASKS if STANDARD_CP_REFACTOR_AFTER_MANUAL else 0
    )
    _gemini_calls = STANDARD_CP_MANUAL_GEMINI_API_CALLS_PER_CASE
    _sessions = STANDARD_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS
    logger.info(
        "STANDARD-CP Gemini: Gemini API %s 回（新規チャット境界 %s）+ Manus リファクタ %s タスク",
        _gemini_calls,
        _sessions,
        _manus_tasks,
    )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_STANDARD_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    outs = StandardCpManualGeminiOutputs()

    p11 = build_standard_cp_gemini_prompt_step_1_1(
        hearing_sheet_content=hearing_sheet_content
    )
    logger.info("STANDARD-CP Gemini: 手順1-1（タブ①）…")
    r11 = model.generate_content(p11, generation_config=gcfg)
    outs.step_1_1 = _response_text(r11)
    outs.raw["step_1_1"] = outs.step_1_1
    outs.raw_prompts["step_1_1"] = p11

    p12_p13 = build_standard_cp_gemini_prompt_step_1_2_and_1_3(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
        existing_site_url=existing_site_url,
        step_1_1_output=outs.step_1_1,
    )

    logger.info("STANDARD-CP Gemini: 手順1-2+1-3 連結（タブ②・1回）…")
    chat2 = model.start_chat(history=[])
    r_tab2 = chat2.send_message(p12_p13, generation_config=gcfg)
    tab2_text = _response_text(r_tab2)
    outs.step_1_2_assistant_ack = ""
    outs.raw["step_1_2"] = ""
    outs.step_1_3 = tab2_text
    outs.raw["step_1_3"] = tab2_text
    outs.raw_prompts["step_1_2"] = p12_p13
    outs.raw_prompts["step_1_3"] = p12_p13

    p2 = build_standard_cp_gemini_prompt_step_2(step_1_3_output=outs.step_1_3)

    logger.info("STANDARD-CP Gemini: 手順2（タブ③）…")
    chat3 = model.start_chat(history=[])
    r2 = chat3.send_message(p2, generation_config=gcfg)
    outs.step_2 = _response_text(r2)
    outs.raw["step_2"] = outs.step_2
    outs.raw_prompts["step_2"] = p2

    p31 = build_standard_cp_gemini_prompt_step_3_1(
        step_2_output=outs.step_2,
        step_1_3_output=outs.step_1_3,
        hearing_sheet_content=hearing_sheet_content,
    )
    p32 = build_standard_cp_gemini_prompt_step_3_2()
    p33 = build_standard_cp_gemini_prompt_step_3_3()
    p34 = build_standard_cp_gemini_prompt_step_3_4()
    p35 = build_standard_cp_gemini_prompt_step_3_5()

    logger.info("STANDARD-CP Gemini: 手順3-1〜3-5（タブ④）…")
    chat4 = model.start_chat(history=[])
    outs.step_3_1 = _response_text(
        chat4.send_message(p31, generation_config=gcfg)
    )
    outs.raw["step_3_1"] = outs.step_3_1
    outs.raw_prompts["step_3_1"] = p31
    outs.step_3_2 = _response_text(chat4.send_message(p32, generation_config=gcfg))
    outs.raw["step_3_2"] = outs.step_3_2
    outs.raw_prompts["step_3_2"] = p32
    outs.step_3_3 = _response_text(chat4.send_message(p33, generation_config=gcfg))
    outs.raw["step_3_3"] = outs.step_3_3
    outs.raw_prompts["step_3_3"] = p33
    outs.step_3_4 = _response_text(chat4.send_message(p34, generation_config=gcfg))
    outs.raw["step_3_4"] = outs.step_3_4
    outs.raw_prompts["step_3_4"] = p34
    outs.step_3_5 = _response_text(chat4.send_message(p35, generation_config=gcfg))
    outs.raw["step_3_5"] = outs.step_3_5
    outs.raw_prompts["step_3_5"] = p35

    p4 = build_standard_cp_gemini_prompt_step_4(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    p6 = build_standard_cp_gemini_prompt_step_6(
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )

    logger.info("STANDARD-CP Gemini: 手順4〜6（タブ⑤）…")
    chat5 = model.start_chat(history=[])
    outs.step_4 = _response_text(chat5.send_message(p4, generation_config=gcfg))
    outs.raw["step_4"] = outs.step_4
    outs.raw_prompts["step_4"] = p4
    p5 = build_standard_cp_gemini_prompt_step_5(
        step_4_output=outs.step_4,
        step_1_3_output=outs.step_1_3,
        step_2_output=outs.step_2,
    )
    outs.step_5_assistant_ack = _response_text(
        chat5.send_message(p5, generation_config=gcfg)
    )
    outs.raw["step_5"] = outs.step_5_assistant_ack
    outs.raw_prompts["step_5"] = p5
    outs.step_6 = _response_text(chat5.send_message(p6, generation_config=gcfg))
    outs.raw["step_6"] = outs.step_6
    outs.raw_prompts["step_6"] = p6

    subpages = (
        "\n\n=== 手順3-2 サービスページ ===\n\n"
        + outs.step_3_2
        + "\n\n=== 手順3-3 会社概要 ===\n\n"
        + outs.step_3_3
        + "\n\n=== 手順3-4 お問い合わせ ===\n\n"
        + outs.step_3_4
        + "\n\n=== 手順3-5 その他 ===\n\n"
        + outs.step_3_5
    )

    p71 = build_standard_cp_gemini_prompt_step_7_1(
        step_6_output=outs.step_6,
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    _tab6_extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    _factual_block = hearing_factual_data_block_for_prompt(
        hearing_sheet_content, extra_texts=_tab6_extras,
    )
    p72 = _subst(
        _load_step("step_7_2.txt"),
        STEP_3_1_OUTPUT=outs.step_3_1,
        STEP_2_OUTPUT=outs.step_2,
        HEARING_FACTUAL_BLOCK=_factual_block,
    )
    p73 = _subst(
        _load_step("step_7_3.txt"),
        STEP_3_SUBPAGES_OUTPUT=subpages,
        HEARING_FACTUAL_BLOCK=_factual_block,
    )
    p74 = _load_step("step_7_4.txt")

    logger.info("STANDARD-CP Gemini: 手順7-1〜7-4（タブ⑥）…")
    chat6 = model.start_chat(history=[])
    outs.step_7_1 = _response_text(chat6.send_message(p71, generation_config=gcfg))
    outs.raw["step_7_1"] = outs.step_7_1
    outs.raw_prompts["step_7_1"] = p71
    outs.step_7_2 = _response_text(chat6.send_message(p72, generation_config=gcfg))
    outs.raw["step_7_2"] = outs.step_7_2
    outs.raw_prompts["step_7_2"] = p72
    outs.step_7_3 = _response_text(chat6.send_message(p73, generation_config=gcfg))
    outs.raw["step_7_3"] = outs.step_7_3
    outs.raw_prompts["step_7_3"] = p73
    outs.step_7_4 = _response_text(chat6.send_message(p74, generation_config=gcfg))
    outs.raw["step_7_4"] = outs.step_7_4
    outs.raw_prompts["step_7_4"] = p74

    canvas_final = (outs.step_7_4 or "").strip() or outs.step_7_3

    _ref_plan = get_contract_plan_info(contract_plan)
    _manus_contract_pages = int(_ref_plan.get("pages") or 6)

    manus_deploy_github_url: str | None = None
    if STANDARD_CP_REFACTOR_AFTER_MANUAL:
        from modules.gemini_manual_common import run_manus_refactor_block

        _extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
        _hr = hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=_extras,
        )
        md, manus_deploy_github_url, _prompt = run_manus_refactor_block(
            canvas_markdown=canvas_final,
            partner_name=partner_name,
            record_number=record_number,
            work_branch=ContractWorkBranch.STANDARD,
            manual_meta_key="standard_cp_manual_gemini",
            model=GEMINI_STANDARD_CP_MODEL,
            steps=outs.raw,
            step_prompts=outs.raw_prompts,
            hearing_reference_block=_hr,
            contract_max_pages=_manus_contract_pages,
            preface_dir=STANDARD_CP_REFACTOR_PREFACE_DIR,
        )
        outs.raw_prompts["manus_refactor_task"] = _prompt
        outs.step_refactor = md
        outs.raw["step_refactor"] = md
        outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    combined = _build_site_build_prompt_from_steps(
        outs,
        partner_name=partner_name,
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )
    plan_info = _ref_plan
    max_pages = int(plan_info.get("pages") or 6)
    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            "modules.standard_cp_gemini_manual: 結合要望テキストが短すぎます（"
            f"{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）。"
        )
    requirements_result: dict[str, Any] = finalize_plain_prompt(
        combined,
        expected_plan_type="standard",
        max_pages=max_pages,
    )
    requirements_result["standard_cp_manual_gemini"] = {
        "model": GEMINI_STANDARD_CP_MODEL,
        "steps": outs.raw,
        "step_prompts": outs.raw_prompts,
    }

    from modules.llm.llm_pipeline_common import assemble_spec_dict_from_requirements

    spec = assemble_spec_dict_from_requirements(
        requirements_result,
        contract_plan,
        partner_name,
    )
    spec["standard_manual_gemini_final"] = canvas_final
    spec["standard_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["standard_manual_gemini_step_2"] = outs.step_2
    spec["standard_manual_gemini_step_6"] = outs.step_6

    logger.info(
        "STANDARD-CP Gemini 完了 model=%s chars_final=%s chars_refactor=%s",
        GEMINI_STANDARD_CP_MODEL,
        len(canvas_final),
        len(outs.step_refactor or ""),
    )
    return requirements_result, spec, outs


def _build_site_build_prompt_from_steps(
    outs: StandardCpManualGeminiOutputs,
    *,
    partner_name: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> str:
    parts: list[str] = [
        f"【STANDARD-CP / Gemini マニュアル結合ログ】パートナー: {partner_name}\n",
        "\n\n=== 手順1-3 ===\n\n",
        outs.step_1_3,
        "\n\n=== 手順2 6ページ構成 ===\n\n",
        outs.step_2,
        "\n\n=== 手順3-1 TOP ===\n\n",
        outs.step_3_1,
        "\n\n=== 手順3-2〜3-5 ===\n\n",
        outs.step_3_2,
        "\n\n",
        outs.step_3_3,
        "\n\n",
        outs.step_3_4,
        "\n\n",
        outs.step_3_5,
        "\n\n=== 手順4 配色 ===\n\n",
        outs.step_4,
        "\n\n=== 手順6 デザイン指示書 ===\n\n",
        outs.step_6,
    ]
    if (hearing_sheet_content or "").strip():
        _memo_extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
        parts.extend(
            [
                "\n\n=== ヒアリング・参考サイト・デザイン（原文抜粋・再掲） ===\n\n",
                hearing_reference_design_block_for_prompt(
                    hearing_sheet_content, extra_texts=_memo_extras,
                ),
                "\n\n=== ヒアリング・事実データ（原文抜粋・再掲） ===\n\n",
                hearing_factual_data_block_for_prompt(
                    hearing_sheet_content, extra_texts=_memo_extras,
                ),
            ]
        )
    return "".join(parts)
