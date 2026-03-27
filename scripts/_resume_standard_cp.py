"""STANDARD-CP パイプラインの途中再開スクリプト。

保存済み llm_steps から最終完了ステップを自動検出し、続きから実行する。
Usage:
    python scripts/_resume_standard_cp.py <record_number>
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.logging_setup import configure_logging

configure_logging()

import logging
from typing import Any

from config.config import (
    OUTPUT_DIR,
    STANDARD_CP_REFACTOR_AFTER_MANUAL,
    get_contract_plan_info,
)
from modules.basic_lp_refactor_claude import STANDARD_CP_REFACTOR_PREFACE_DIR
from modules.case_extraction import extract_hearing_bundle
from modules.contract_workflow import ContractWorkBranch, resolve_contract_work_branch
from modules.hearing_url_utils import (
    hearing_factual_data_block_for_prompt,
    hearing_reference_design_block_for_prompt,
)
from modules.llm.llm_pipeline_common import (
    MIN_SITE_BUILD_PROMPT_CHARS,
    assemble_spec_dict_from_requirements,
    finalize_plain_prompt,
)
from modules.llm.llm_raw_output import write_llm_raw_artifacts_phase2_snapshot
from modules.llm.llm_step_trace import _step_seq, begin_case_llm_trace, end_case_llm_trace
from modules.standard_cp_claude_manual import (
    CLAUDE_STANDARD_CP_MODEL,
    StandardCpManualClaudeOutputs,
    _build_site_build_prompt_from_steps,
    _MODULE_NAME,
    _new_chat,
    _gen,
    _run_reference_url_extraction,
    _subst,
    _load_step,
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
    detect_blog_desired,
)
from modules.basic_lp_refactor_claude import BASIC_LP_REFACTOR_MANUS_TASKS
from main import WebsiteBot

logger = logging.getLogger("resume_standard_cp")


def _read_step(record: str, step_num: int, kind: str, name: str) -> str:
    p = OUTPUT_DIR / record / "llm_steps" / f"{step_num:03d}_claude_cli_{kind}" / name
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")


def _out(record: str, step: int, kind: str) -> str:
    return _read_step(record, step, kind, "output.md")


def _inp(record: str, step: int, kind: str) -> str:
    return _read_step(record, step, kind, "input.md")


def _detect_last_step(record: str) -> int:
    steps_dir = OUTPUT_DIR / record / "llm_steps"
    if not steps_dir.is_dir():
        return 0
    nums = []
    for d in steps_dir.iterdir():
        if d.is_dir() and (d / "output.md").is_file():
            try:
                nums.append(int(d.name[:3]))
            except ValueError:
                pass
    return max(nums) if nums else 0


def resume_case(record_number: str) -> None:
    last_step = _detect_last_step(record_number)
    if last_step == 0:
        logger.error("保存済みステップが見つかりません: %s", record_number)
        sys.exit(1)

    logger.info("最終完了ステップ: %03d → 次から再開", last_step)

    bot = WebsiteBot()
    case = bot.spreadsheet.get_case_by_record_number(record_number)
    if case is None:
        logger.error("レコード %s が見つかりません", record_number)
        sys.exit(1)

    logger.info(
        "再開: record=%s row=%s partner=%s plan=%s",
        record_number, case["row_number"], case["partner_name"], case["contract_plan"],
    )
    bot.spreadsheet.update_ai_status(case["row_number"], "MacBot")

    bundle = extract_hearing_bundle(
        case, fetch_hearing_sheet=bot.spec_generator.fetch_hearing_sheet,
    )
    hs = bundle.hearing_sheet_content
    am = bundle.appo_memo
    sn = bundle.sales_notes

    outs = StandardCpManualClaudeOutputs()

    # --- 保存済み出力を復元 ---
    if last_step >= 1:
        outs.step_1_1 = _out(record_number, 1, "generate")
        outs.raw["step_1_1"] = outs.step_1_1
        outs.raw_prompts["step_1_1"] = _inp(record_number, 1, "generate")
    if last_step >= 2:
        outs.step_1_3 = _out(record_number, 2, "chat")
        outs.raw["step_1_2"] = ""
        outs.raw["step_1_3"] = outs.step_1_3
        outs.raw_prompts["step_1_2"] = _inp(record_number, 2, "chat")
        outs.raw_prompts["step_1_3"] = _inp(record_number, 2, "chat")
    if last_step >= 3:
        outs.step_2 = _out(record_number, 3, "chat")
        outs.raw["step_2"] = outs.step_2
        outs.raw_prompts["step_2"] = _inp(record_number, 3, "chat")
    if last_step >= 4:
        outs.step_3_1 = _out(record_number, 4, "chat")
        outs.raw["step_3_1"] = outs.step_3_1
        outs.raw_prompts["step_3_1"] = _inp(record_number, 4, "chat")
    if last_step >= 5:
        outs.step_3_2 = _out(record_number, 5, "chat")
        outs.raw["step_3_2"] = outs.step_3_2
        outs.raw_prompts["step_3_2"] = _inp(record_number, 5, "chat")
    if last_step >= 6:
        outs.step_3_3 = _out(record_number, 6, "chat")
        outs.raw["step_3_3"] = outs.step_3_3
        outs.raw_prompts["step_3_3"] = _inp(record_number, 6, "chat")
    if last_step >= 7:
        outs.step_3_4 = _out(record_number, 7, "chat")
        outs.raw["step_3_4"] = outs.step_3_4
        outs.raw_prompts["step_3_4"] = _inp(record_number, 7, "chat")
    if last_step >= 8:
        outs.step_3_5 = _out(record_number, 8, "chat")
        outs.raw["step_3_5"] = outs.step_3_5
        outs.raw_prompts["step_3_5"] = _inp(record_number, 8, "chat")
    if last_step >= 9:
        outs.step_url_hearing = _out(record_number, 9, "generate")
        outs.raw["step_url_hearing"] = outs.step_url_hearing
        outs.raw_prompts["step_url_hearing"] = _inp(record_number, 9, "generate")
    if last_step >= 10:
        outs.step_url_appo = _out(record_number, 10, "generate")
        outs.raw["step_url_appo"] = outs.step_url_appo
        outs.raw_prompts["step_url_appo"] = _inp(record_number, 10, "generate")
    if last_step >= 11:
        outs.step_4 = _out(record_number, 11, "chat")
        outs.raw["step_4"] = outs.step_4
        outs.raw_prompts["step_4"] = _inp(record_number, 11, "chat")
    if last_step >= 12:
        outs.step_5_assistant_ack = _out(record_number, 12, "chat")
        outs.raw["step_5"] = outs.step_5_assistant_ack
        outs.raw_prompts["step_5"] = _inp(record_number, 12, "chat")
    if last_step >= 13:
        outs.step_6 = _out(record_number, 13, "chat")
        outs.raw["step_6"] = outs.step_6
        outs.raw_prompts["step_6"] = _inp(record_number, 13, "chat")
    if last_step >= 14:
        outs.step_7_1 = _out(record_number, 14, "chat")
        outs.raw["step_7_1"] = outs.step_7_1
        outs.raw_prompts["step_7_1"] = _inp(record_number, 14, "chat")
    if last_step >= 15:
        outs.step_7_2 = _out(record_number, 15, "chat")
        outs.raw["step_7_2"] = outs.step_7_2
        outs.raw_prompts["step_7_2"] = _inp(record_number, 15, "chat")
    if last_step >= 16:
        outs.step_7_3 = _out(record_number, 16, "chat")
        outs.raw["step_7_3"] = outs.step_7_3
        outs.raw_prompts["step_7_3"] = _inp(record_number, 16, "chat")
    if last_step >= 17:
        outs.step_7_4 = _out(record_number, 17, "chat")
        outs.raw["step_7_4"] = outs.step_7_4
        outs.raw_prompts["step_7_4"] = _inp(record_number, 17, "chat")

    begin_case_llm_trace(record_number)
    _step_seq.set(last_step)

    # --- タブ④ 途中再開 (step 3-4 〜 3-5) ---
    if last_step < 8:
        tab4_history: list[dict[str, str]] = []
        for s, k in [(4, "step_3_1"), (5, "step_3_2"), (6, "step_3_3"), (7, "step_3_4")]:
            if s > last_step:
                break
            tab4_history.append({"role": "user", "content": _inp(record_number, s, "chat")})
            tab4_history.append({"role": "assistant", "content": _out(record_number, s, "chat")})

        chat4 = _new_chat(history=tab4_history)

        if last_step < 7:
            logger.info("再開: 手順3-4（タブ④）…")
            p34 = build_standard_cp_claude_prompt_step_3_4()
            outs.step_3_4 = chat4.send_message(p34)
            outs.raw["step_3_4"] = outs.step_3_4
            outs.raw_prompts["step_3_4"] = p34

        if last_step < 8:
            logger.info("再開: 手順3-5（タブ④）…")
            p35 = build_standard_cp_claude_prompt_step_3_5()
            outs.step_3_5 = chat4.send_message(p35)
            outs.raw["step_3_5"] = outs.step_3_5
            outs.raw_prompts["step_3_5"] = p35

    # --- 参考サイト URL 抽出 ---
    if last_step < 10:
        logger.info("再開: 参考サイト URL 抽出…")
        ref_block, _all_urls, _url_raws, _url_prompts = _run_reference_url_extraction(
            hearing_text=(hs or "").strip(),
            appo_memo=am,
            sales_notes=sn,
            model=CLAUDE_STANDARD_CP_MODEL,
            module_name=_MODULE_NAME,
        )
        for k, v in _url_raws.items():
            setattr(outs, k, v)
            outs.raw[k] = v
        for k, v in _url_prompts.items():
            outs.raw_prompts[k] = v
    else:
        ref_block = ""

    # --- タブ⑤ (step 4 〜 6) ---
    if last_step < 13:
        if last_step < 11:
            p4 = build_standard_cp_claude_prompt_step_4(
                hearing_sheet_content=hs, appo_memo=am, sales_notes=sn,
                reference_url_block_override=ref_block,
            )
            logger.info("再開: 手順4（タブ⑤）…")
            chat5 = _new_chat()
            outs.step_4 = chat5.send_message(p4)
            outs.raw["step_4"] = outs.step_4
            outs.raw_prompts["step_4"] = p4
        else:
            tab5_history: list[dict[str, str]] = []
            for s in range(11, min(last_step + 1, 14)):
                tab5_history.append({"role": "user", "content": _inp(record_number, s, "chat")})
                tab5_history.append({"role": "assistant", "content": _out(record_number, s, "chat")})
            chat5 = _new_chat(history=tab5_history)

        if last_step < 12:
            p5 = build_standard_cp_claude_prompt_step_5(
                step_4_output=outs.step_4, step_1_3_output=outs.step_1_3,
                step_2_output=outs.step_2,
            )
            logger.info("再開: 手順5（タブ⑤）…")
            outs.step_5_assistant_ack = chat5.send_message(p5)
            outs.raw["step_5"] = outs.step_5_assistant_ack
            outs.raw_prompts["step_5"] = p5

        if last_step < 13:
            p6 = build_standard_cp_claude_prompt_step_6(
                hearing_sheet_content=hs, appo_memo=am, sales_notes=sn,
            )
            logger.info("再開: 手順6（タブ⑤）…")
            outs.step_6 = chat5.send_message(p6)
            outs.raw["step_6"] = outs.step_6
            outs.raw_prompts["step_6"] = p6

    # --- タブ⑥ (step 7-1 〜 7-5) ---
    batch1 = (
        "\n\n=== 手順3-2 サービスページ ===\n\n" + outs.step_3_2
        + "\n\n=== 手順3-3 会社概要 ===\n\n" + outs.step_3_3
    )
    batch2 = (
        "\n\n=== 手順3-4 お問い合わせ ===\n\n" + outs.step_3_4
        + "\n\n=== 手順3-5 その他 ===\n\n" + outs.step_3_5
    )
    _tab6_extras = [s for s in (am, sn) if (s or "").strip()]
    _factual_block = hearing_factual_data_block_for_prompt(hs, extra_texts=_tab6_extras)

    if last_step < 17:
        if last_step < 14:
            p71 = build_standard_cp_claude_prompt_step_7_1(
                step_6_output=outs.step_6,
                hearing_sheet_content=hs, appo_memo=am, sales_notes=sn,
            )
            logger.info("再開: 手順7-1（タブ⑥）…")
            chat6 = _new_chat()
            outs.step_7_1 = chat6.send_message(p71)
            outs.raw["step_7_1"] = outs.step_7_1
            outs.raw_prompts["step_7_1"] = p71
        else:
            tab6_history: list[dict[str, str]] = []
            for s in range(14, min(last_step + 1, 18)):
                tab6_history.append({"role": "user", "content": _inp(record_number, s, "chat")})
                tab6_history.append({"role": "assistant", "content": _out(record_number, s, "chat")})
            chat6 = _new_chat(history=tab6_history)

        if last_step < 15:
            p72 = _subst(
                _load_step("step_7_2.txt"),
                STEP_3_1_OUTPUT=outs.step_3_1, STEP_2_OUTPUT=outs.step_2,
                HEARING_FACTUAL_BLOCK=_factual_block,
            )
            logger.info("再開: 手順7-2（タブ⑥）…")
            outs.step_7_2 = chat6.send_message(p72)
            outs.raw["step_7_2"] = outs.step_7_2
            outs.raw_prompts["step_7_2"] = p72

        if last_step < 16:
            p73 = _subst(
                _load_step("step_7_3.txt"),
                STEP_3_LOWER_BATCH1=batch1, HEARING_FACTUAL_BLOCK=_factual_block,
            )
            logger.info("再開: 手順7-3（タブ⑥）…")
            outs.step_7_3 = chat6.send_message(p73)
            outs.raw["step_7_3"] = outs.step_7_3
            outs.raw_prompts["step_7_3"] = p73

        if last_step < 17:
            p74 = _subst(
                _load_step("step_7_4.txt"),
                STEP_3_LOWER_BATCH2=batch2, HEARING_FACTUAL_BLOCK=_factual_block,
            )
            logger.info("再開: 手順7-4（タブ⑥）…")
            outs.step_7_4 = chat6.send_message(p74)
            outs.raw["step_7_4"] = outs.step_7_4
            outs.raw_prompts["step_7_4"] = p74

    p75 = _load_step("step_7_5.txt")
    logger.info("再開: 手順7-5（タブ⑥・最終仕上げ）…")
    if last_step >= 14:
        tab6_final_history: list[dict[str, str]] = []
        for s in range(14, 18):
            u = _inp(record_number, s, "chat") or outs.raw_prompts.get(f"step_7_{s-13}", "")
            a = _out(record_number, s, "chat") or getattr(outs, f"step_7_{s-13}", "")
            if u and a:
                tab6_final_history.append({"role": "user", "content": u})
                tab6_final_history.append({"role": "assistant", "content": a})
        chat6 = _new_chat(history=tab6_final_history)
    outs.step_7_5 = chat6.send_message(p75)
    outs.raw["step_7_5"] = outs.step_7_5
    outs.raw_prompts["step_7_5"] = p75

    canvas_final = (outs.step_7_5 or "").strip() or outs.step_7_4

    # --- Manus リファクタ ---
    manus_deploy_github_url: str | None = None
    if STANDARD_CP_REFACTOR_AFTER_MANUAL:
        from modules.claude_manual_common import run_manus_refactor_block

        _extras = [s for s in (am, sn) if (s or "").strip()]
        _hr = hearing_reference_design_block_for_prompt(hs, extra_texts=_extras)
        plan_info = get_contract_plan_info((case.get("contract_plan") or "").strip())
        max_pages = int(plan_info.get("pages") or 6)

        md, manus_deploy_github_url, _prompt = run_manus_refactor_block(
            canvas_markdown=canvas_final,
            partner_name=case["partner_name"],
            record_number=record_number,
            work_branch=ContractWorkBranch.STANDARD,
            manual_meta_key="standard_cp_manual_claude",
            model=CLAUDE_STANDARD_CP_MODEL,
            steps=outs.raw,
            step_prompts=outs.raw_prompts,
            hearing_reference_block=_hr,
            contract_max_pages=max_pages,
            preface_dir=STANDARD_CP_REFACTOR_PREFACE_DIR,
        )
        outs.raw_prompts["manus_refactor_task"] = _prompt
        outs.step_refactor = md
        outs.raw["step_refactor"] = md
        outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    # --- spec 組み立て ---
    combined = _build_site_build_prompt_from_steps(
        outs, partner_name=case["partner_name"],
        hearing_sheet_content=hs, appo_memo=am, sales_notes=sn,
    )
    plan_info = get_contract_plan_info((case.get("contract_plan") or "").strip())
    max_pages = int(plan_info.get("pages") or 6)

    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(f"結合要望テキストが短すぎます（{len(combined)}）")

    req: dict[str, Any] = finalize_plain_prompt(
        combined, expected_plan_type="standard", max_pages=max_pages,
    )
    req["standard_cp_manual_claude"] = {
        "model": CLAUDE_STANDARD_CP_MODEL,
        "steps": outs.raw,
        "step_prompts": outs.raw_prompts,
    }

    spec = assemble_spec_dict_from_requirements(
        req, case.get("contract_plan", ""), case["partner_name"],
    )
    spec["standard_manual_claude_final"] = canvas_final
    spec["standard_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["standard_manual_claude_step_2"] = outs.step_2
    spec["standard_manual_claude_step_6"] = outs.step_6

    site_name = f"{case['partner_name']}-{case['record_number']}"
    write_llm_raw_artifacts_phase2_snapshot(
        site_name=site_name, spec=spec, requirements_result=req,
        work_branch=ContractWorkBranch.STANDARD,
    )
    end_case_llm_trace()

    # --- Phase 3-5 ---
    work_branch = resolve_contract_work_branch(case["contract_plan"])
    site_dir = bot._phase3_prepare_site(case, req, spec, work_branch)
    bot._phase4_build(case, spec, site_dir, work_branch, plan_info)
    deploy_url = bot._phase5_deploy(case, spec, site_dir)
    logger.info("再開完了: record=%s deploy=%s", record_number, deploy_url)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/_resume_standard_cp.py <record_number>")
        sys.exit(1)
    resume_case(sys.argv[1])
