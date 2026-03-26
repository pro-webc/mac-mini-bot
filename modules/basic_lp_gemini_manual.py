"""BASIC LP 制作マニュアルに沿った Gemini 多段チェーン。

**API 呼び出し回数（既存マニュアルの「新規チャット」「タブ」境界と一致）**

- 合計 **11 回**（各回が ``generate_content`` または ``send_message`` の1回）
- **新規チャット（コンテキスト断絶）** はマニュアルの **タブ1〜5** に対応し **5 回**

内訳（1 + 1 + 3 + 3 + 3 = 11）:

- **タブ1**（新規チャット1回目）: 手順1-1 → 1回
- **タブ2**（新規チャット2回目）: 手順1-2 と 1-3（``step_1_3_nonrecruit.txt``）を **1メッセージに連結** → 1回（手作業マニュアルと同じ）
- **タブ3**（新規チャット3回目）: 手順2 → 3 → 4 → 3回
- **タブ4**（新規チャット4回目）: 手順5 → 6 → 7 → 3回
- **タブ5**（新規チャット5回目）: 手順8-1 → 8-2 → 8-3 → 3回

**手順8の「複数タブ」について（勘違い防止）**

マニュアルには、手順8について「同じプロンプトを複数タブで試し、良い案を選ぶ」旨がある。
これは **人手での任意の反復**であり、**必須の工程ではない**。
本モジュールは **タブ5を1本分**だけ実行する（上表の 8-1〜8-3 の **3 回のみ**）。
複数案の生成・比較を自動で増やす API 呼び出しは行わない。

**リファクタ段階（任意・既定オン）**

環境変数 ``BASIC_LP_REFACTOR_AFTER_MANUAL=true``（既定）のとき、手順8の出力のあと **Manus API（タスク1件）**で
``config/prompts/manus/`` のオーケストレーション＋リファクタ指示に従い **複数ファイルのリファクタ後ソース**をテキストで生成する（Gemini マニュアル本体とは別サービス）。

プロンプト本文は ``config/prompts/basic_lp_manual/*.txt`` にマニュアル準拠で格納する。
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import google.generativeai as genai
from config.config import (
    BASIC_LP_REFACTOR_AFTER_MANUAL,
    BASIC_LP_USE_GEMINI_MANUAL,
    GEMINI_BASIC_LP_MODEL,
    get_contract_plan_info,
)

from modules.basic_lp_refactor_gemini import BASIC_LP_REFACTOR_MANUS_TASKS
from modules.contract_workflow import ContractWorkBranch
from modules.hearing_url_utils import hearing_reference_design_block_for_prompt
from modules.llm.basic_lp_spec import build_basic_lp_spec_dict
from modules.llm.llm_pipeline_common import MIN_SITE_BUILD_PROMPT_CHARS, finalize_plain_prompt

logger = logging.getLogger(__name__)

# マニュアル「タブ1〜5」＝新規チャット5回、Gemini API は計11回（手順8の任意・複数タブは含まない）
BASIC_LP_MANUAL_GEMINI_API_CALLS_PER_CASE = 11
BASIC_LP_MANUAL_GEMINI_NEW_CHAT_SESSIONS = 5
# リファクタ段階は Manus タスク1件（BASIC_LP_REFACTOR_AFTER_MANUAL 時）

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

_MODULE_NAME = "modules.basic_lp_gemini_manual"
_MANUAL_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_lp_manual"


def _load_step(filename: str) -> str:
    return _load_step_impl(_MANUAL_DIR, filename, module_name=_MODULE_NAME)


def _subst(template: str, **kwargs: str) -> str:
    return _subst_impl(template, module_name=_MODULE_NAME, **kwargs)


def _hearing_block(hearing_sheet_content: str) -> str:
    return _hearing_block_impl(hearing_sheet_content, module_name=_MODULE_NAME)


def _response_text(response: Any) -> str:
    return _response_text_impl(response, module_name=_MODULE_NAME)


@dataclass
class BasicLpManualGeminiOutputs:
    """各手順のモデル出力（デバッグ・追跡用）。"""

    step_1_1: str = ""
    step_1_2_assistant_ack: str = ""
    step_1_3: str = ""
    step_2: str = ""
    step_3: str = ""
    step_4: str = ""
    step_5: str = ""
    step_6_assistant_ack: str = ""
    step_7: str = ""
    step_8_1: str = ""
    step_8_2: str = ""
    step_8_3: str = ""
    step_refactor: str = ""
    raw: dict[str, str] = field(default_factory=dict)
    raw_prompts: dict[str, str] = field(default_factory=dict)


def run_basic_lp_gemini_manual_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    record_number: str = "",
    existing_site_url: str = "",
) -> tuple[dict[str, Any], dict[str, Any], BasicLpManualGeminiOutputs]:
    """
    マニュアル手順どおりに Gemini を呼び、``requirements_result`` / ``spec`` を組み立てる。

    Returns:
        (requirements_result, spec, step_outputs)
    """
    if not BASIC_LP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.basic_lp_gemini_manual: BASIC_LP_USE_GEMINI_MANUAL が無効です。"
        )
    _manus_tasks = (
        BASIC_LP_REFACTOR_MANUS_TASKS if BASIC_LP_REFACTOR_AFTER_MANUAL else 0
    )
    _gemini_calls = BASIC_LP_MANUAL_GEMINI_API_CALLS_PER_CASE
    _sessions = BASIC_LP_MANUAL_GEMINI_NEW_CHAT_SESSIONS
    logger.info(
        "BASIC LP Gemini: Gemini API %s 回（新規チャット境界 %s）+ Manus リファクタ %s タスク。"
        " 手順8の複数タブによる追加案生成は含みません。",
        _gemini_calls,
        _sessions,
        _manus_tasks,
    )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_BASIC_LP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    outs = BasicLpManualGeminiOutputs()

    hear = _hearing_block(hearing_sheet_content)
    p11 = _subst(_load_step("step_1_1.txt"), HEARING_BLOCK=hear)
    logger.info("BASIC LP Gemini: 手順1-1（タブ1・単発）…")
    r11 = model.generate_content(p11, generation_config=gcfg)
    outs.step_1_1 = _response_text(r11)
    outs.raw["step_1_1"] = outs.step_1_1
    outs.raw_prompts["step_1_1"] = p11

    ap_block = (appo_memo or "").strip()
    if (sales_notes or "").strip():
        ap_block += (
            "\n\n【営業メモ・その他先方情報（マニュアル「用意する情報」の補足）】\n"
            + (sales_notes or "").strip()
        )
    p12 = _subst(
        _load_step("step_1_2.txt"),
        STEP_1_1_OUTPUT=outs.step_1_1,
        APPO_MEMO=ap_block or "（なし）",
        EXISTING_SITE_URL_BLOCK=_existing_site_url_block(hear, existing_site_url),
    )
    p13 = _load_step("step_1_3_nonrecruit.txt")
    p12_p13 = f"{p12.rstrip()}\n\n{p13.lstrip()}"

    logger.info("BASIC LP Gemini: 手順1-2+1-3 連結（タブ2・1回）…")
    chat2 = model.start_chat(history=[])
    r_tab2 = chat2.send_message(p12_p13, generation_config=gcfg)
    tab2_text = _response_text(r_tab2)
    outs.step_1_2_assistant_ack = ""
    outs.raw["step_1_2"] = ""
    outs.step_1_3 = tab2_text
    outs.raw["step_1_3"] = tab2_text
    outs.raw_prompts["step_1_2"] = p12_p13
    outs.raw_prompts["step_1_3"] = p12_p13

    p2 = _subst(
        _load_step("step_2.txt"),
        STEP_1_3_OUTPUT=outs.step_1_3,
    )
    p3 = _load_step("step_3.txt")
    p4 = _load_step("step_4.txt")

    logger.info("BASIC LP Gemini: 手順2〜4（タブ3・同一チャット）…")
    chat3 = model.start_chat(history=[])
    r2 = chat3.send_message(p2, generation_config=gcfg)
    outs.step_2 = _response_text(r2)
    outs.raw["step_2"] = outs.step_2
    outs.raw_prompts["step_2"] = p2
    r3 = chat3.send_message(p3, generation_config=gcfg)
    outs.step_3 = _response_text(r3)
    outs.raw["step_3"] = outs.step_3
    outs.raw_prompts["step_3"] = p3
    r4 = chat3.send_message(p4, generation_config=gcfg)
    outs.step_4 = _response_text(r4)
    outs.raw["step_4"] = outs.step_4
    outs.raw_prompts["step_4"] = p4

    hp_c, mood_c = _client_hp_and_mood_placeholders()
    p5 = _subst(
        _load_step("step_5.txt"),
        HP_COLOR_CLIENT=hp_c,
        MOOD_CLIENT=mood_c,
        REFERENCE_URL_BLOCK=_reference_url_block(
            hear, extra_texts=[s for s in (appo_memo, sales_notes) if (s or "").strip()],
        ),
    )
    _extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    _hr_block = hearing_reference_design_block_for_prompt(
        hearing_sheet_content, extra_texts=_extras,
    )
    p7 = _subst(
        _load_step("step_7.txt"),
        HEARING_REFERENCE_DESIGN_BLOCK=_hr_block,
    )

    logger.info("BASIC LP Gemini: 手順5〜7（タブ4・同一チャット）…")
    chat4 = model.start_chat(history=[])
    r5 = chat4.send_message(p5, generation_config=gcfg)
    outs.step_5 = _response_text(r5)
    outs.raw["step_5"] = outs.step_5
    outs.raw_prompts["step_5"] = p5
    p6 = _subst(
        _load_step("step_6.txt"),
        HEARING_1_3_OUTPUT=outs.step_1_3,
        STEP_4_OUTPUT=outs.step_4,
        STEP_5_OUTPUT=outs.step_5,
        HEARING_REFERENCE_DESIGN_BLOCK=_hr_block,
    )
    r6 = chat4.send_message(p6, generation_config=gcfg)
    outs.step_6_assistant_ack = _response_text(r6)
    outs.raw["step_6"] = outs.step_6_assistant_ack
    outs.raw_prompts["step_6"] = p6
    r7 = chat4.send_message(p7, generation_config=gcfg)
    outs.step_7 = _response_text(r7)
    outs.raw["step_7"] = outs.step_7
    outs.raw_prompts["step_7"] = p7

    p81 = _subst(
        _load_step("step_8_1.txt"),
        STEP_7_OUTPUT=outs.step_7,
        STEP_4_OUTPUT=outs.step_4,
        HEARING_REFERENCE_DESIGN_BLOCK=_hr_block,
    )
    p82 = _subst(
        _load_step("step_8_2.txt"),
        STEP_4_OUTPUT=outs.step_4,
    )
    p83 = _load_step("step_8_3.txt")

    logger.info("BASIC LP Gemini: 手順8-1〜8-3（タブ5・同一チャット）…")
    chat5 = model.start_chat(history=[])
    r81 = chat5.send_message(p81, generation_config=gcfg)
    outs.step_8_1 = _response_text(r81)
    outs.raw["step_8_1"] = outs.step_8_1
    outs.raw_prompts["step_8_1"] = p81
    r82 = chat5.send_message(p82, generation_config=gcfg)
    outs.step_8_2 = _response_text(r82)
    outs.raw["step_8_2"] = outs.step_8_2
    outs.raw_prompts["step_8_2"] = p82
    r83 = chat5.send_message(p83, generation_config=gcfg)
    outs.step_8_3 = _response_text(r83)
    outs.raw["step_8_3"] = outs.step_8_3
    outs.raw_prompts["step_8_3"] = p83

    _ref_plan = get_contract_plan_info(contract_plan)
    _manus_contract_pages = int(_ref_plan.get("pages") or 1)

    manus_deploy_github_url: str | None = None
    if BASIC_LP_REFACTOR_AFTER_MANUAL:
        from modules.gemini_manual_common import run_manus_refactor_block

        md, manus_deploy_github_url, _prompt = run_manus_refactor_block(
            canvas_markdown=outs.step_8_3,
            partner_name=partner_name,
            record_number=record_number,
            work_branch=ContractWorkBranch.BASIC_LP,
            manual_meta_key="basic_lp_manual_gemini",
            model=GEMINI_BASIC_LP_MODEL,
            steps=outs.raw,
            step_prompts=outs.raw_prompts,
            hearing_reference_block=_hr_block,
            contract_max_pages=_manus_contract_pages,
        )
        outs.raw_prompts["manus_refactor_task"] = _prompt
        outs.step_refactor = md
        outs.raw["step_refactor"] = md
        outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    combined = _build_site_build_prompt_from_steps(
        outs,
        partner_name=partner_name,
        hearing_sheet_content=hearing_sheet_content,
    )
    plan_info = _ref_plan
    max_pages = int(plan_info.get("pages") or 1)
    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            "modules.basic_lp_gemini_manual: 結合要望テキストが短すぎます（"
            f"{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）。"
        )
    requirements_result: dict[str, Any] = finalize_plain_prompt(
        combined,
        expected_plan_type="basic_lp",
        max_pages=max_pages,
    )
    requirements_result["basic_lp_manual_gemini"] = {
        "model": GEMINI_BASIC_LP_MODEL,
        "steps": outs.raw,
        "step_prompts": outs.raw_prompts,
    }

    spec = build_basic_lp_spec_dict(
        requirements_result,
        contract_plan,
        partner_name,
    )
    spec["basic_lp_manual_gemini_final"] = outs.step_8_3
    spec["basic_lp_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["basic_lp_manual_gemini_step_4_wireframe"] = outs.step_4
    spec["basic_lp_manual_gemini_step_7_design_doc"] = outs.step_7

    logger.info(
        "BASIC LP Gemini マニュアルチェーン完了 model=%s chars_8_3=%s chars_refactor=%s",
        GEMINI_BASIC_LP_MODEL,
        len(outs.step_8_3),
        len(outs.step_refactor or ""),
    )
    return requirements_result, spec, outs


def _build_site_build_prompt_from_steps(
    outs: BasicLpManualGeminiOutputs,
    *,
    partner_name: str,
    hearing_sheet_content: str = "",
) -> str:
    parts: list[str] = [
        f"【BASIC LP / Gemini マニュアル全手順の結合ログ】パートナー: {partner_name}\n",
        "\n\n=== 手順1-1 ===\n\n",
        outs.step_1_1,
        "\n\n=== 手順1-3 ===\n\n",
        outs.step_1_3,
        "\n\n=== 手順2 マーケ分析 ===\n\n",
        outs.step_2,
        "\n\n=== 手順3 構成 ===\n\n",
        outs.step_3,
        "\n\n=== 手順4 原稿・画像指示 ===\n\n",
        outs.step_4,
        "\n\n=== 手順5 配色・雰囲気 ===\n\n",
        outs.step_5,
        "\n\n=== 手順7 デザイン指示書 ===\n\n",
        outs.step_7,
    ]
    if (hearing_sheet_content or "").strip():
        parts.extend(
            [
                "\n\n=== ヒアリング・参考サイト・デザイン（原文抜粋・再掲） ===\n\n",
                hearing_reference_design_block_for_prompt(hearing_sheet_content),
            ]
        )
    return "".join(parts)
