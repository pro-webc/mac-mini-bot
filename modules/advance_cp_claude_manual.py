"""ADVANCE-CP（コーポレート・12ページ想定）制作マニュアルに沿った Claude 多段チェーン。

**CLI 呼び出し回数（マニュアルの「新規チャット」「タブ」境界と一致）**

- 合計 **15 回**（各回が Claude Code CLI（claude -p）の1回）
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

from config.config import (
    ADVANCE_CP_INCLUDE_BLOG_PAGE,
    ADVANCE_CP_REFACTOR_AFTER_MANUAL,
    ADVANCE_CP_USE_CLAUDE_MANUAL,
    CLAUDE_ADVANCE_CP_MODEL,
    get_contract_plan_info,
)
from modules.case_extraction import detect_blog_desired

from modules.basic_lp_refactor_claude import (
    ADVANCE_CP_REFACTOR_PREFACE_DIR,
    BASIC_LP_REFACTOR_MANUS_TASKS,
)
from modules.contract_workflow import ContractWorkBranch
from modules.hearing_url_utils import (
    hearing_factual_data_block_for_prompt,
    hearing_reference_design_block_for_prompt,
)
from modules.llm.llm_pipeline_common import MIN_SITE_BUILD_PROMPT_CHARS, finalize_plain_prompt

logger = logging.getLogger(__name__)

ADVANCE_CP_MANUAL_CLAUDE_API_CALLS_PER_CASE = 16
ADVANCE_CP_MANUAL_CLAUDE_NEW_CHAT_SESSIONS = 6

from modules.claude_manual_common import (
    ClaudeCLIChat,
    generate_text as _generate_text,
    hearing_block as _hearing_block_impl,
    existing_site_url_block as _existing_site_url_block,
    client_hp_and_mood_placeholders as _client_hp_and_mood_placeholders,
    run_reference_url_extraction as _run_reference_url_extraction,
    load_step as _load_step_impl,
    subst as _subst_impl,
)

_MODULE_NAME = "modules.advance_cp_claude_manual"
_MANUAL_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "advance_cp_manual"


def _load_step(filename: str) -> str:
    return _load_step_impl(_MANUAL_DIR, filename, module_name=_MODULE_NAME)


def _subst(template: str, **kwargs: str) -> str:
    return _subst_impl(template, module_name=_MODULE_NAME, **kwargs)


def _hearing_block(hearing_sheet_content: str) -> str:
    return _hearing_block_impl(hearing_sheet_content, module_name=_MODULE_NAME)


def _gen(prompt: str) -> str:
    """単発生成のショートハンド。"""
    return _generate_text(
        prompt,
        model=CLAUDE_ADVANCE_CP_MODEL,
        module_name=_MODULE_NAME,
    )


def _new_chat() -> ClaudeCLIChat:
    """マルチターンチャットのショートハンド。"""
    return ClaudeCLIChat(
        model=CLAUDE_ADVANCE_CP_MODEL,
        module_name=_MODULE_NAME,
    )


def _blog_page_line(include_blog: bool | None = None) -> str:
    flag = include_blog if include_blog is not None else ADVANCE_CP_INCLUDE_BLOG_PAGE
    if flag:
        return "・ブログページは必ず独立1ページ(不必要の場合は必ず削除)\n"
    return ""


@dataclass
class AdvanceCpManualClaudeOutputs:
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
    step_url_hearing: str = ""
    step_url_appo: str = ""
    step_url_sales: str = ""
    step_refactor: str = ""
    raw: dict[str, str] = field(default_factory=dict)
    raw_prompts: dict[str, str] = field(default_factory=dict)


def run_advance_cp_claude_manual_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    record_number: str = "",
    existing_site_url: str = "",
) -> tuple[dict[str, Any], dict[str, Any], AdvanceCpManualClaudeOutputs]:
    if not ADVANCE_CP_USE_CLAUDE_MANUAL:
        raise RuntimeError(
            "modules.advance_cp_claude_manual: ADVANCE_CP_USE_CLAUDE_MANUAL が無効です。"
        )
    _manus_tasks = (
        BASIC_LP_REFACTOR_MANUS_TASKS if ADVANCE_CP_REFACTOR_AFTER_MANUAL else 0
    )
    _claude_calls = ADVANCE_CP_MANUAL_CLAUDE_API_CALLS_PER_CASE
    _sessions = ADVANCE_CP_MANUAL_CLAUDE_NEW_CHAT_SESSIONS
    logger.info(
        "ADVANCE-CP Claude: Claude API %s 回（新規チャット境界 %s）+ Manus リファクタ %s タスク",
        _claude_calls,
        _sessions,
        _manus_tasks,
    )
    outs = AdvanceCpManualClaudeOutputs()

    hear = _hearing_block(hearing_sheet_content)
    p11 = _subst(_load_step("step_1_1.txt"), HEARING_BLOCK=hear)
    logger.info("ADVANCE-CP Claude: 手順1-1（タブ①）…")
    outs.step_1_1 = _gen(p11)
    outs.raw["step_1_1"] = outs.step_1_1
    outs.raw_prompts["step_1_1"] = p11

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

    logger.info("ADVANCE-CP Claude: 手順1-2+1-3 連結（タブ②・1回）…")
    chat2 = _new_chat()
    tab2_text = chat2.send_message(p12_p13)
    outs.step_1_2_assistant_ack = ""
    outs.raw["step_1_2"] = ""
    outs.step_1_3 = tab2_text
    outs.raw["step_1_3"] = tab2_text
    outs.raw_prompts["step_1_2"] = p12_p13
    outs.raw_prompts["step_1_3"] = p12_p13

    _blog = detect_blog_desired(hearing_sheet_content, appo_memo, sales_notes)
    logger.info("ブログページ: %s（全情報源から自動判定）", "含める" if _blog else "含めない")
    p2 = _subst(
        _load_step("step_2.txt"),
        STEP_1_3_OUTPUT=outs.step_1_3,
        BLOG_PAGE_LINE=_blog_page_line(_blog),
    )

    logger.info("ADVANCE-CP Claude: 手順2（タブ③）…")
    chat3 = _new_chat()
    outs.step_2 = chat3.send_message(p2)
    outs.raw["step_2"] = outs.step_2
    outs.raw_prompts["step_2"] = p2

    hear = (hearing_sheet_content or "").strip()
    hb = (
        hear
        if hear
        else "（ヒアリング原文の再掲なし。以下お客様情報のみ参照すること。）"
    )
    p31 = _subst(
        _load_step("step_3_1.txt"),
        STEP_2_OUTPUT=outs.step_2,
        STEP_1_3_OUTPUT=outs.step_1_3,
        HEARING_BLOCK=hb,
    )
    p32 = _load_step("step_3_2.txt")
    p33 = _load_step("step_3_3.txt")
    p34 = _load_step("step_3_4.txt")
    p35 = _load_step("step_3_5.txt")

    logger.info("ADVANCE-CP Claude: 手順3-1〜3-5（タブ④）…")
    chat4 = _new_chat()
    outs.step_3_1 = chat4.send_message(p31)
    outs.raw["step_3_1"] = outs.step_3_1
    outs.raw_prompts["step_3_1"] = p31
    outs.step_3_2 = chat4.send_message(p32)
    outs.raw["step_3_2"] = outs.step_3_2
    outs.raw_prompts["step_3_2"] = p32
    outs.step_3_3 = chat4.send_message(p33)
    outs.raw["step_3_3"] = outs.step_3_3
    outs.raw_prompts["step_3_3"] = p33
    outs.step_3_4 = chat4.send_message(p34)
    outs.raw["step_3_4"] = outs.step_3_4
    outs.raw_prompts["step_3_4"] = p34
    outs.step_3_5 = chat4.send_message(p35)
    outs.raw["step_3_5"] = outs.step_3_5
    outs.raw_prompts["step_3_5"] = p35

    # --- 参考サイト URL 抽出（LLM 工程: ヒアリング / アポメモ / 営業メモ → URL 一覧） ---
    # 引数: hear / appo_memo / sales_notes の生テキスト
    # 処理: 非空ソースごとに Claude CLI 単発で参考サイト URL を JSON 抽出
    # 出力: ref_block（プロンプト埋め込み用テキスト）/ raw・prompt 辞書（outs 保存用）
    ref_block, _all_urls, _url_raws, _url_prompts = _run_reference_url_extraction(
        hearing_text=hear,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
        model=CLAUDE_ADVANCE_CP_MODEL,
        module_name=_MODULE_NAME,
    )
    for k, v in _url_raws.items():
        setattr(outs, k, v)
        outs.raw[k] = v
    for k, v in _url_prompts.items():
        outs.raw_prompts[k] = v

    hp_c, mood_c = _client_hp_and_mood_placeholders()
    p4 = _subst(
        _load_step("step_4.txt"),
        HP_COLOR_CLIENT=hp_c,
        MOOD_CLIENT=mood_c,
        REFERENCE_URL_BLOCK=ref_block,
    )
    _extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    p6 = _subst(
        _load_step("step_6.txt"),
        HEARING_REFERENCE_DESIGN_BLOCK=hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=_extras,
        ),
    )

    logger.info("ADVANCE-CP Claude: 手順4〜6（タブ⑤）…")
    chat5 = _new_chat()
    outs.step_4 = chat5.send_message(p4)
    outs.raw["step_4"] = outs.step_4
    outs.raw_prompts["step_4"] = p4
    p5 = _subst(
        _load_step("step_5.txt"),
        STEP_4_OUTPUT=outs.step_4,
        HEARING_1_3_OUTPUT=outs.step_1_3,
        STEP_2_OUTPUT=outs.step_2,
    )
    outs.step_5_assistant_ack = chat5.send_message(p5)
    outs.raw["step_5"] = outs.step_5_assistant_ack
    outs.raw_prompts["step_5"] = p5
    outs.step_6 = chat5.send_message(p6)
    outs.raw["step_6"] = outs.step_6
    outs.raw_prompts["step_6"] = p6

    batch1 = (
        "\n\n=== 手順3-2 サービスページ ===\n\n"
        + outs.step_3_2
        + "\n\n=== 手順3-3 会社概要 ===\n\n"
        + outs.step_3_3
        + "\n\n=== 手順3-4 お問い合わせ ===\n\n"
        + outs.step_3_4
    )
    batch2 = "\n\n=== 手順3-5 その他 ===\n\n" + outs.step_3_5

    p71 = _subst(
        _load_step("step_7_1.txt"),
        STEP_6_OUTPUT=outs.step_6,
        HEARING_REFERENCE_DESIGN_BLOCK=hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=_extras,
        ),
    )
    _factual = hearing_factual_data_block_for_prompt(
        hearing_sheet_content, extra_texts=_extras,
    )
    p72 = _subst(
        _load_step("step_7_2.txt"),
        STEP_3_1_OUTPUT=outs.step_3_1,
        STEP_2_OUTPUT=outs.step_2,
        HEARING_FACTUAL_BLOCK=_factual,
    )
    p73 = _subst(
        _load_step("step_7_3.txt"),
        STEP_3_LOWER_BATCH1=batch1,
        HEARING_FACTUAL_BLOCK=_factual,
    )
    p74 = _subst(
        _load_step("step_7_4.txt"),
        STEP_3_LOWER_BATCH2=batch2,
        HEARING_FACTUAL_BLOCK=_factual,
    )

    logger.info("ADVANCE-CP Claude: 手順7-1〜7-4（タブ⑥）…")
    chat6 = _new_chat()
    outs.step_7_1 = chat6.send_message(p71)
    outs.raw["step_7_1"] = outs.step_7_1
    outs.raw_prompts["step_7_1"] = p71
    outs.step_7_2 = chat6.send_message(p72)
    outs.raw["step_7_2"] = outs.step_7_2
    outs.raw_prompts["step_7_2"] = p72
    outs.step_7_3 = chat6.send_message(p73)
    outs.raw["step_7_3"] = outs.step_7_3
    outs.raw_prompts["step_7_3"] = p73
    outs.step_7_4 = chat6.send_message(p74)
    outs.raw["step_7_4"] = outs.step_7_4
    outs.raw_prompts["step_7_4"] = p74

    canvas_final = (outs.step_7_4 or "").strip() or outs.step_7_3

    _ref_plan = get_contract_plan_info(contract_plan)
    _manus_contract_pages = int(_ref_plan.get("pages") or 12)

    manus_deploy_github_url: str | None = None
    if ADVANCE_CP_REFACTOR_AFTER_MANUAL:
        from modules.claude_manual_common import run_manus_refactor_block

        _hr = hearing_reference_design_block_for_prompt(
            hearing_sheet_content, extra_texts=_extras,
        )
        md, manus_deploy_github_url, _prompt = run_manus_refactor_block(
            canvas_markdown=canvas_final,
            partner_name=partner_name,
            record_number=record_number,
            work_branch=ContractWorkBranch.ADVANCE,
            manual_meta_key="advance_cp_manual_claude",
            model=CLAUDE_ADVANCE_CP_MODEL,
            steps=outs.raw,
            step_prompts=outs.raw_prompts,
            hearing_reference_block=_hr,
            contract_max_pages=_manus_contract_pages,
            preface_dir=ADVANCE_CP_REFACTOR_PREFACE_DIR,
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
    max_pages = int(plan_info.get("pages") or 12)
    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            "modules.advance_cp_claude_manual: 結合要望テキストが短すぎます（"
            f"{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）。"
        )
    requirements_result: dict[str, Any] = finalize_plain_prompt(
        combined,
        expected_plan_type="advance",
        max_pages=max_pages,
    )
    requirements_result["advance_cp_manual_claude"] = {
        "model": CLAUDE_ADVANCE_CP_MODEL,
        "steps": outs.raw,
        "step_prompts": outs.raw_prompts,
    }

    from modules.llm.llm_pipeline_common import assemble_spec_dict_from_requirements

    spec = assemble_spec_dict_from_requirements(
        requirements_result,
        contract_plan,
        partner_name,
    )
    spec["advance_manual_claude_final"] = canvas_final
    spec["advance_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["advance_manual_claude_step_2"] = outs.step_2
    spec["advance_manual_claude_step_6"] = outs.step_6

    logger.info(
        "ADVANCE-CP Claude 完了 model=%s chars_final=%s chars_refactor=%s",
        CLAUDE_ADVANCE_CP_MODEL,
        len(canvas_final),
        len(outs.step_refactor or ""),
    )
    return requirements_result, spec, outs


def _build_site_build_prompt_from_steps(
    outs: AdvanceCpManualClaudeOutputs,
    *,
    partner_name: str,
    hearing_sheet_content: str = "",
    appo_memo: str = "",
    sales_notes: str = "",
) -> str:
    parts: list[str] = [
        f"【ADVANCE-CP / Claude マニュアル結合ログ】パートナー: {partner_name}\n",
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
