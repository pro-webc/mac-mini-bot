"""BASIC-CP（コーポレート1ページ）制作マニュアルに沿った Gemini 多段チェーン。

**API 呼び出し回数（マニュアルの「新規チャット」「タブ」境界と一致）**

- 合計 **11 回**（各回が ``generate_content`` または ``send_message`` の1回）
- **新規チャット（コンテキスト断絶）** はマニュアルの **タブ①〜⑤** に対応し **5 回**

内訳（1 + 2 + 2 + 3 + 3 = 11）:

- **タブ①**: 手順1-1 → 1回
- **タブ②**: 手順1-2 → 1-3 → 2回
- **タブ③**: 手順2 → 3 → 2回（構成プロンプトのみ。手順4はタブ④）
- **タブ④**: 手順4 → 5 → 6 → 3回（雰囲気・配色 → デザイン指示書）
- **タブ⑤**: 手順7-1 → 7-2 → 7-3 → 3回（コード生成。Canvas 想定）

**手順7の「複数タブで3パターン」について**

マニュアルでは同じプロンプトを複数タブで試し良い案を選ぶ旨があるが、**人手での任意反復**であり必須ではない。
本モジュールは **タブ⑤を1本分**だけ実行する（7-1〜7-3 の **3 回のみ**）。

**リファクタ段階（任意・既定オン）**

``BASIC_CP_REFACTOR_AFTER_MANUAL=true``（既定）のとき、手順7-3 のあと **新規チャット1回**で
``basic_lp_refactor/refactoring_instruction.txt``（LP と共通）と ``basic_cp_refactor/preface_intro.txt`` + 共通 ``preface_shared.txt`` に従いリファクタする（**+1 回** API）。

プロンプト本文は ``config/prompts/basic_cp_manual/*.txt`` に格納する。
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import google.generativeai as genai
from config.config import (
    BASIC_CP_REFACTOR_AFTER_MANUAL,
    BASIC_CP_USE_GEMINI_MANUAL,
    GEMINI_API_KEY,
    GEMINI_BASIC_CP_MODEL,
    get_contract_plan_info,
)
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from modules.basic_lp_refactor_gemini import (
    BASIC_CP_REFACTOR_PREFACE_DIR,
    BASIC_LP_REFACTOR_GEMINI_API_CALLS,
    run_basic_lp_refactor_stage,
)
from modules.basic_text_llm import build_basic_spec_dict
from modules.gemini_generative_timeout import ensure_gemini_rpc_patch_from_config
from modules.llm_mock import MIN_SITE_BUILD_PROMPT_CHARS, finalize_plain_prompt

logger = logging.getLogger(__name__)

BASIC_CP_MANUAL_GEMINI_API_CALLS_PER_CASE = 11
BASIC_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS = 5

_MANUAL_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_cp_manual"

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
            f"modules.basic_cp_gemini_manual: マニュアルプロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def _subst(template: str, **kwargs: str) -> str:
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", value)
    if "{{" in out and "}}" in out:
        i = out.index("{{")
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: プレースホルダが未置換です: "
            + out[i : i + 80]
        )
    return out


def _configure() -> None:
    key = (GEMINI_API_KEY or "").strip()
    if not key:
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: GEMINI_API_KEY が空です。"
        )
    genai.configure(api_key=key)
    ensure_gemini_rpc_patch_from_config()


def _gen_config() -> dict[str, Any]:
    return {
        "max_output_tokens": 8192,
        "temperature": 0.35,
    }


def _response_text(response: Any) -> str:
    if not getattr(response, "candidates", None):
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: Gemini 応答に candidates がありません。"
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
            "modules.basic_cp_gemini_manual: Gemini 応答テキストが空です（フィルタ等でブロックされた可能性があります）。"
        )
    return out


# --- ヒアリング・参考URL（basic_lp_gemini_manual と同趣旨） ---


def _first_http_url(text: str) -> str:
    m = re.search(r"https?://[^\s\]\)\"'<>]+", text or "")
    return m.group(0).rstrip(".,;") if m else ""


def _hearing_block(hearing_sheet_content: str) -> str:
    h = (hearing_sheet_content or "").strip()
    if not h:
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: ヒアリングシート本文が空です（手順1-1 に渡せません）。"
        )
    return h


def _existing_site_url_block(hearing_sheet_content: str, explicit: str) -> str:
    u = (explicit or "").strip()
    if not u:
        u = _first_http_url(hearing_sheet_content)
    if u:
        return u
    return "（既存サイトURLの記載なし。ヒアリング本文に URL があればそちらを参照）"


def _client_hp_and_mood_placeholders() -> tuple[str, str]:
    return (
        "（ヒアリングシート設問「ホームページに使いたい色」および手順1-3の記載を最優先。未記載なら本文から判断）",
        "（ヒアリングシート設問「希望の雰囲気」および手順1-3の記載を最優先。未記載なら本文から判断）",
    )


def _reference_url_block(hearing_sheet_content: str) -> str:
    u = _first_http_url(hearing_sheet_content or "")
    if u:
        return u
    return "（参考サイトURLの記載なし。手順1-3およびヒアリング本文を参照）"


@dataclass
class BasicCpManualGeminiOutputs:
    """各手順のモデル出力（デバッグ・追跡用）。"""

    step_1_1: str = ""
    step_1_2_assistant_ack: str = ""
    step_1_3: str = ""
    step_2: str = ""
    step_3: str = ""
    step_4: str = ""
    step_5_assistant_ack: str = ""
    step_6: str = ""
    step_7_1: str = ""
    step_7_2: str = ""
    step_7_3: str = ""
    step_refactor: str = ""
    raw: dict[str, str] = field(default_factory=dict)


def run_basic_cp_gemini_manual_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    existing_site_url: str = "",
) -> tuple[dict[str, Any], dict[str, Any], BasicCpManualGeminiOutputs]:
    """
    BASIC-CP マニュアル手順どおりに Gemini を呼び、``requirements_result`` / ``spec`` を組み立てる。

    Returns:
        (requirements_result, spec, step_outputs)
    """
    if not BASIC_CP_USE_GEMINI_MANUAL:
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: BASIC_CP_USE_GEMINI_MANUAL が無効です。"
        )
    _ref_extra = (
        BASIC_LP_REFACTOR_GEMINI_API_CALLS if BASIC_CP_REFACTOR_AFTER_MANUAL else 0
    )
    _api_total = BASIC_CP_MANUAL_GEMINI_API_CALLS_PER_CASE + _ref_extra
    _sessions = BASIC_CP_MANUAL_GEMINI_NEW_CHAT_SESSIONS + (
        1 if BASIC_CP_REFACTOR_AFTER_MANUAL else 0
    )
    logger.info(
        "BASIC-CP Gemini: API を合計 %s 回呼び出します（マニュアル %s 回 + リファクタ %s 回、"
        "新規チャット境界 %s 回・手順7の複数タブによる追加案生成は含みません）",
        _api_total,
        BASIC_CP_MANUAL_GEMINI_API_CALLS_PER_CASE,
        _ref_extra,
        _sessions,
    )
    _configure()
    model = genai.GenerativeModel(
        GEMINI_BASIC_CP_MODEL,
        safety_settings=_SAFETY,
    )
    gcfg = _gen_config()
    outs = BasicCpManualGeminiOutputs()

    hear = _hearing_block(hearing_sheet_content)
    p11 = _subst(_load_step("step_1_1.txt"), HEARING_BLOCK=hear)
    logger.info("BASIC-CP Gemini: 手順1-1（タブ①・単発）…")
    r11 = model.generate_content(p11, generation_config=gcfg)
    outs.step_1_1 = _response_text(r11)
    outs.raw["step_1_1"] = outs.step_1_1

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
    p13 = _load_step("step_1_3.txt")

    logger.info("BASIC-CP Gemini: 手順1-2 / 1-3（タブ②・同一チャット）…")
    chat2 = model.start_chat(history=[])
    r12 = chat2.send_message(p12, generation_config=gcfg)
    outs.step_1_2_assistant_ack = _response_text(r12)
    outs.raw["step_1_2"] = outs.step_1_2_assistant_ack
    r13 = chat2.send_message(p13, generation_config=gcfg)
    outs.step_1_3 = _response_text(r13)
    outs.raw["step_1_3"] = outs.step_1_3

    p2 = _subst(
        _load_step("step_2.txt"),
        STEP_1_3_OUTPUT=outs.step_1_3,
    )
    p3 = _load_step("step_3.txt")

    logger.info("BASIC-CP Gemini: 手順2〜3（タブ③・同一チャット）…")
    chat3 = model.start_chat(history=[])
    r2 = chat3.send_message(p2, generation_config=gcfg)
    outs.step_2 = _response_text(r2)
    outs.raw["step_2"] = outs.step_2
    r3 = chat3.send_message(p3, generation_config=gcfg)
    outs.step_3 = _response_text(r3)
    outs.raw["step_3"] = outs.step_3

    hp_c, mood_c = _client_hp_and_mood_placeholders()
    p4 = _subst(
        _load_step("step_4.txt"),
        HP_COLOR_CLIENT=hp_c,
        MOOD_CLIENT=mood_c,
        REFERENCE_URL_BLOCK=_reference_url_block(hear),
    )
    p5 = _subst(
        _load_step("step_5.txt"),
        HEARING_1_3_OUTPUT=outs.step_1_3,
        STEP_2_OUTPUT=outs.step_2,
    )
    p6 = _load_step("step_6.txt")

    logger.info("BASIC-CP Gemini: 手順4〜6（タブ④・同一チャット）…")
    chat4 = model.start_chat(history=[])
    r4 = chat4.send_message(p4, generation_config=gcfg)
    outs.step_4 = _response_text(r4)
    outs.raw["step_4"] = outs.step_4
    r5 = chat4.send_message(p5, generation_config=gcfg)
    outs.step_5_assistant_ack = _response_text(r5)
    outs.raw["step_5"] = outs.step_5_assistant_ack
    r6 = chat4.send_message(p6, generation_config=gcfg)
    outs.step_6 = _response_text(r6)
    outs.raw["step_6"] = outs.step_6

    p71 = _subst(
        _load_step("step_7_1.txt"),
        STEP_6_OUTPUT=outs.step_6,
    )
    p72 = _subst(
        _load_step("step_7_2.txt"),
        STEP_3_OUTPUT=outs.step_3,
    )
    p73 = _load_step("step_7_3.txt")

    logger.info("BASIC-CP Gemini: 手順7-1〜7-3（タブ⑤・同一チャット）…")
    chat5 = model.start_chat(history=[])
    r71 = chat5.send_message(p71, generation_config=gcfg)
    outs.step_7_1 = _response_text(r71)
    outs.raw["step_7_1"] = outs.step_7_1
    r72 = chat5.send_message(p72, generation_config=gcfg)
    outs.step_7_2 = _response_text(r72)
    outs.raw["step_7_2"] = outs.step_7_2
    r73 = chat5.send_message(p73, generation_config=gcfg)
    outs.step_7_3 = _response_text(r73)
    outs.raw["step_7_3"] = outs.step_7_3

    if BASIC_CP_REFACTOR_AFTER_MANUAL:
        outs.step_refactor = run_basic_lp_refactor_stage(
            canvas_source_code=outs.step_7_3,
            model=model,
            generation_config=gcfg,
            response_text_fn=_response_text,
            preface_dir=BASIC_CP_REFACTOR_PREFACE_DIR,
        )
        outs.raw["step_refactor"] = outs.step_refactor

    combined = _build_site_build_prompt_from_steps(outs, partner_name=partner_name)
    plan_info = get_contract_plan_info(contract_plan)
    max_pages = int(plan_info.get("pages") or 1)
    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            "modules.basic_cp_gemini_manual: 結合要望テキストが短すぎます（"
            f"{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）。"
        )
    requirements_result: dict[str, Any] = finalize_plain_prompt(
        combined,
        expected_plan_type="basic",
        max_pages=max_pages,
    )
    requirements_result["basic_cp_manual_gemini"] = {
        "model": GEMINI_BASIC_CP_MODEL,
        "steps": outs.raw,
    }

    spec = build_basic_spec_dict(
        requirements_result,
        contract_plan,
        partner_name,
    )
    spec["basic_manual_gemini_final"] = outs.step_7_3
    spec["basic_refactored_source_markdown"] = outs.step_refactor or ""
    spec["basic_manual_gemini_step_2_structure"] = outs.step_2
    spec["basic_manual_gemini_step_6_design_doc"] = outs.step_6

    logger.info(
        "BASIC-CP Gemini マニュアルチェーン完了 model=%s chars_7_3=%s chars_refactor=%s",
        GEMINI_BASIC_CP_MODEL,
        len(outs.step_7_3),
        len(outs.step_refactor or ""),
    )
    return requirements_result, spec, outs


def _build_site_build_prompt_from_steps(
    outs: BasicCpManualGeminiOutputs,
    *,
    partner_name: str,
) -> str:
    parts: list[str] = [
        f"【BASIC-CP / Gemini マニュアル全手順の結合ログ】パートナー: {partner_name}\n",
        "\n\n=== 手順1-1 ===\n\n",
        outs.step_1_1,
        "\n\n=== 手順1-3 ===\n\n",
        outs.step_1_3,
        "\n\n=== 手順2 サイト構成 ===\n\n",
        outs.step_2,
        "\n\n=== 手順3 セクション内容 ===\n\n",
        outs.step_3,
        "\n\n=== 手順4 配色・雰囲気 ===\n\n",
        outs.step_4,
        "\n\n=== 手順6 デザイン指示書 ===\n\n",
        outs.step_6,
    ]
    return "".join(parts)
