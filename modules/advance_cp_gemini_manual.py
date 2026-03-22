"""ADVANCE-CP（コーポレート・12ページ想定）制作マニュアルに沿った Gemini 多段チェーン。

**API 呼び出し回数（マニュアルの「新規チャット」「タブ」境界と一致）**

- 合計 **15 回**（各回が ``generate_content`` または ``send_message`` の1回）
- **新規チャット** はマニュアルの **タブ①〜⑥** に対応し **6 回**

内訳（1 + 1 + 1 + 5 + 3 + 4 = 15）:

- **タブ①**: 手順1-1 → 1回
- **タブ②**: 手順1-2 と 1-3 を **1メッセージに連結**して送信 → 1回（手作業マニュアルと同じ）
- **タブ③**: 手順2（12ページ構成）→ 1回
- **タブ④**: 手順3-1 → … → 3-5 → 5回（ページ別・同一チャット）
- **タブ⑤**: 手順4 → 5 → 6 → 3回（配色・デザイン指示書）
- **タブ⑥**: 手順7-1 → 7-2 → 7-3 → 7-4 → 4回（コード・Canvas 想定）

**手順7-3 / 7-4**: 下層ページを2群に分け、7-3 は手順3-2・3-3・3-4、7-4 は手順3-5 の構成を渡す。

**リファクタ**（任意・既定オン）: ``ADVANCE_CP_REFACTOR_AFTER_MANUAL`` で **Manus タスク1件**。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import google.generativeai as genai
from config.config import (
    ADVANCE_CP_INCLUDE_BLOG_PAGE,
    ADVANCE_CP_REFACTOR_AFTER_MANUAL,
    ADVANCE_CP_USE_GEMINI_MANUAL,
    GEMINI_ADVANCE_CP_MODEL,
    GEMINI_API_KEY,
    GEMINI_MANUAL_MAX_OUTPUT_TOKENS,
    get_contract_plan_info,
)
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from modules.basic_lp_refactor_gemini import (
    ADVANCE_CP_REFACTOR_PREFACE_DIR,
    BASIC_LP_REFACTOR_MANUS_TASKS,
    run_basic_lp_refactor_stage,
)
from modules.gemini_generative_timeout import ensure_gemini_rpc_patch_from_config
from modules.hearing_url_utils import (
    existing_site_url_guess_from_hearing,
    reference_site_url_from_hearing,
)
from modules.llm.llm_pipeline_common import MIN_SITE_BUILD_PROMPT_CHARS, finalize_plain_prompt

logger = logging.getLogger(__name__)

ADVANCE_CP_MANUAL_GEMINI_API_CALLS_PER_CASE = 16
ADVANCE_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS = 6

_MANUAL_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "advance_cp_manual"

_SAFETY = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


def _load_step(filename: str) -> str:
    path = _MANUAL_DIR / filename
    if not path.is_file():
        raise RuntimeError(
            f"modules.advance_cp_gemini_manual: マニュアルプロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def _subst(template: str, **kwargs: str) -> str:
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", value)
    if "{{" in out and "}}" in out:
        i = out.index("{{")
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: プレースホルダが未置換です: "
            + out[i : i + 80]
        )
    return out


def _configure() -> None:
    key = (GEMINI_API_KEY or "").strip()
    if not key:
        raise RuntimeError("modules.advance_cp_gemini_manual: GEMINI_API_KEY が空です。")
    genai.configure(api_key=key)
    ensure_gemini_rpc_patch_from_config()


def _gen_config() -> dict[str, Any]:
    return {
        "max_output_tokens": GEMINI_MANUAL_MAX_OUTPUT_TOKENS,
        "temperature": 0.35,
    }


def _response_text(response: Any) -> str:
    if not getattr(response, "candidates", None):
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: Gemini 応答に candidates がありません。"
            f" prompt_feedback={getattr(response, 'prompt_feedback', None)}"
        )
    chunks: list[str] = []
    for cand in response.candidates:
        content = getattr(cand, "content", None)
        if not content or not getattr(content, "parts", None):
            continue
        for part in content.parts:
            t = getattr(part, "text", None)
            if t:
                chunks.append(t)
    out = "".join(chunks).strip()
    if not out:
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: Gemini 応答テキストが空です。"
        )
    return out


def _hearing_block(hearing_sheet_content: str) -> str:
    h = (hearing_sheet_content or "").strip()
    if not h:
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: ヒアリングシート本文が空です。"
        )
    return h


def _existing_site_url_block(hearing_sheet_content: str, explicit: str) -> str:
    u = (explicit or "").strip()
    if not u:
        u = existing_site_url_guess_from_hearing(hearing_sheet_content)
    if u:
        return u
    return "（既存サイトURLの記載なし。ヒアリング本文に URL があればそちらを参照）"


def _client_hp_and_mood_placeholders() -> tuple[str, str]:
    return (
        "（ヒアリングシート設問「ホームページに使いたい色」および手順1-3の記載を最優先。未記載なら本文から判断）",
        "（ヒアリングシート設問「希望の雰囲気」および手順1-3の記載を最優先。未記載なら本文から判断）",
    )


def _reference_url_block(hearing_sheet_content: str) -> str:
    u = reference_site_url_from_hearing(hearing_sheet_content or "")
    if u:
        return u
    return "（参考サイトURLの記載なし。手順1-3およびヒアリング本文を参照）"


def _blog_page_line() -> str:
    if ADVANCE_CP_INCLUDE_BLOG_PAGE:
        return "・ブログページは必ず独立1ページ(不必要の場合は必ず削除)\n"
    return ""


@dataclass
class AdvanceCpManualGeminiOutputs:
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


def run_advance_cp_gemini_manual_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    record_number: str = "",
    existing_site_url: str = "",
) -> tuple[dict[str, Any], dict[str, Any], AdvanceCpManualGeminiOutputs]:
    if not ADVANCE_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: ADVANCE_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _manus_tasks = (
        BASIC_LP_REFACTOR_MANUS_TASKS if ADVANCE_CP_REFACTOR_AFTER_MANUAL else 0
    )
    _gemini_calls = ADVANCE_CP_MANUAL_GEMINI_API_CALLS_PER_CASE
    _sessions = ADVANCE_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS
    logger.info(
        "ADVANCE-CP Gemini: Gemini API %s 回（新規チャット境界 %s）+ Manus リファクタ %s タスク",
        _gemini_calls,
        _sessions,
        _manus_tasks,
    )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_ADVANCE_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    outs = AdvanceCpManualGeminiOutputs()

    hear = _hearing_block(hearing_sheet_content)
    p11 = _subst(_load_step("step_1_1.txt"), HEARING_BLOCK=hear)
    logger.info("ADVANCE-CP Gemini: 手順1-1（タブ①）…")
    r11 = model.generate_content(p11, generation_config=gcfg)
    outs.step_1_1 = _response_text(r11)
    outs.raw["step_1_1"] = outs.step_1_1

    ap_block = (appo_memo or "").strip()
    if (sales_notes or "").strip():
        ap_block += (
            "\n\n【営業メモ・その他先方情報】\n"
            + (sales_notes or "").strip()
        )
    p12 = _subst(
        _load_step("step_1_2.txt"),
        STEP_1_1_OUTPUT=outs.step_1_1,
        APPO_MEMO=ap_block or "（なし）",
        EXISTING_SITE_URL_BLOCK=_existing_site_url_block(hear, existing_site_url),
    )
    p13 = _load_step("step_1_3.txt")
    p12_p13 = f"{p12.rstrip()}\n\n{p13.lstrip()}"

    logger.info("ADVANCE-CP Gemini: 手順1-2+1-3 連結（タブ②・1回）…")
    chat2 = model.start_chat(history=[])
    r_tab2 = chat2.send_message(p12_p13, generation_config=gcfg)
    tab2_text = _response_text(r_tab2)
    outs.step_1_2_assistant_ack = ""
    outs.raw["step_1_2"] = ""
    outs.step_1_3 = tab2_text
    outs.raw["step_1_3"] = tab2_text

    p2 = _subst(
        _load_step("step_2.txt"),
        STEP_1_3_OUTPUT=outs.step_1_3,
        BLOG_PAGE_LINE=_blog_page_line(),
    )

    logger.info("ADVANCE-CP Gemini: 手順2（タブ③）…")
    chat3 = model.start_chat(history=[])
    r2 = chat3.send_message(p2, generation_config=gcfg)
    outs.step_2 = _response_text(r2)
    outs.raw["step_2"] = outs.step_2

    p31 = _subst(
        _load_step("step_3_1.txt"),
        STEP_2_OUTPUT=outs.step_2,
        STEP_1_3_OUTPUT=outs.step_1_3,
    )
    p32 = _load_step("step_3_2.txt")
    p33 = _load_step("step_3_3.txt")
    p34 = _load_step("step_3_4.txt")
    p35 = _load_step("step_3_5.txt")

    logger.info("ADVANCE-CP Gemini: 手順3-1〜3-5（タブ④）…")
    chat4 = model.start_chat(history=[])
    outs.step_3_1 = _response_text(
        chat4.send_message(p31, generation_config=gcfg)
    )
    outs.raw["step_3_1"] = outs.step_3_1
    outs.step_3_2 = _response_text(chat4.send_message(p32, generation_config=gcfg))
    outs.raw["step_3_2"] = outs.step_3_2
    outs.step_3_3 = _response_text(chat4.send_message(p33, generation_config=gcfg))
    outs.raw["step_3_3"] = outs.step_3_3
    outs.step_3_4 = _response_text(chat4.send_message(p34, generation_config=gcfg))
    outs.raw["step_3_4"] = outs.step_3_4
    outs.step_3_5 = _response_text(chat4.send_message(p35, generation_config=gcfg))
    outs.raw["step_3_5"] = outs.step_3_5

    hp_c, mood_c = _client_hp_and_mood_placeholders()
    p4 = _subst(
        _load_step("step_4.txt"),
        HP_COLOR_CLIENT=hp_c,
        MOOD_CLIENT=mood_c,
        REFERENCE_URL_BLOCK=_reference_url_block(hear),
    )
    p6 = _load_step("step_6.txt")

    logger.info("ADVANCE-CP Gemini: 手順4〜6（タブ⑤）…")
    chat5 = model.start_chat(history=[])
    outs.step_4 = _response_text(chat5.send_message(p4, generation_config=gcfg))
    outs.raw["step_4"] = outs.step_4
    p5 = _subst(
        _load_step("step_5.txt"),
        STEP_4_OUTPUT=outs.step_4,
        HEARING_1_3_OUTPUT=outs.step_1_3,
        STEP_2_OUTPUT=outs.step_2,
    )
    outs.step_5_assistant_ack = _response_text(
        chat5.send_message(p5, generation_config=gcfg)
    )
    outs.raw["step_5"] = outs.step_5_assistant_ack
    outs.step_6 = _response_text(chat5.send_message(p6, generation_config=gcfg))
    outs.raw["step_6"] = outs.step_6

    batch1 = (
        "\n\n=== 手順3-2 サービスページ ===\n\n"
        + outs.step_3_2
        + "\n\n=== 手順3-3 会社概要 ===\n\n"
        + outs.step_3_3
        + "\n\n=== 手順3-4 お問い合わせ ===\n\n"
        + outs.step_3_4
    )
    batch2 = "\n\n=== 手順3-5 その他 ===\n\n" + outs.step_3_5

    p71 = _subst(_load_step("step_7_1.txt"), STEP_6_OUTPUT=outs.step_6)
    p72 = _subst(
        _load_step("step_7_2.txt"),
        STEP_3_1_OUTPUT=outs.step_3_1,
        STEP_2_OUTPUT=outs.step_2,
    )
    p73 = _subst(
        _load_step("step_7_3.txt"),
        STEP_3_LOWER_BATCH1=batch1,
    )
    p74 = _subst(
        _load_step("step_7_4.txt"),
        STEP_3_LOWER_BATCH2=batch2,
    )

    logger.info("ADVANCE-CP Gemini: 手順7-1〜7-4（タブ⑥）…")
    chat6 = model.start_chat(history=[])
    outs.step_7_1 = _response_text(chat6.send_message(p71, generation_config=gcfg))
    outs.raw["step_7_1"] = outs.step_7_1
    outs.step_7_2 = _response_text(chat6.send_message(p72, generation_config=gcfg))
    outs.raw["step_7_2"] = outs.step_7_2
    outs.step_7_3 = _response_text(chat6.send_message(p73, generation_config=gcfg))
    outs.raw["step_7_3"] = outs.step_7_3
    outs.step_7_4 = _response_text(chat6.send_message(p74, generation_config=gcfg))
    outs.raw["step_7_4"] = outs.step_7_4

    canvas_final = (outs.step_7_4 or "").strip() or outs.step_7_3

    manus_deploy_github_url: str | None = None
    if ADVANCE_CP_REFACTOR_AFTER_MANUAL:
        md, manus_deploy_github_url = run_basic_lp_refactor_stage(
            canvas_source_code=canvas_final,
            preface_dir=ADVANCE_CP_REFACTOR_PREFACE_DIR,
            partner_name=partner_name,
            record_number=record_number,
        )
        outs.step_refactor = md
        outs.raw["step_refactor"] = md
        outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    combined = _build_site_build_prompt_from_steps(outs, partner_name=partner_name)
    plan_info = get_contract_plan_info(contract_plan)
    max_pages = int(plan_info.get("pages") or 12)
    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            "modules.advance_cp_gemini_manual: 結合要望テキストが短すぎます（"
            f"{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）。"
        )
    requirements_result: dict[str, Any] = finalize_plain_prompt(
        combined,
        expected_plan_type="advance",
        max_pages=max_pages,
    )
    requirements_result["advance_cp_manual_gemini"] = {
        "model": GEMINI_ADVANCE_CP_MODEL,
        "steps": outs.raw,
    }

    from modules.llm.llm_pipeline_common import assemble_spec_dict_from_requirements

    spec = assemble_spec_dict_from_requirements(
        requirements_result,
        contract_plan,
        partner_name,
    )
    spec["advance_manual_gemini_final"] = canvas_final
    spec["advance_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["advance_manual_gemini_step_2"] = outs.step_2
    spec["advance_manual_gemini_step_6"] = outs.step_6

    logger.info(
        "ADVANCE-CP Gemini 完了 model=%s chars_final=%s chars_refactor=%s",
        GEMINI_ADVANCE_CP_MODEL,
        len(canvas_final),
        len(outs.step_refactor or ""),
    )
    return requirements_result, spec, outs


def _build_site_build_prompt_from_steps(
    outs: AdvanceCpManualGeminiOutputs,
    *,
    partner_name: str,
) -> str:
    parts: list[str] = [
        f"【ADVANCE-CP / Gemini マニュアル結合ログ】パートナー: {partner_name}\n",
        "\n\n=== 手順1-3 ===\n\n",
        outs.step_1_3,
        "\n\n=== 手順2 12ページ構成 ===\n\n",
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
    return "".join(parts)
