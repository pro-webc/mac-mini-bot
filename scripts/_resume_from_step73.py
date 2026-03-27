"""STANDARD-CP step 7-3 タイムアウト案件の途中再開スクリプト。

#16308・#16536 は step 7-3 で Claude CLI がタイムアウト (900s) したが、
steps 001-015 (step 7-2 まで) の出力は保存済み。
このスクリプトは保存済み出力を読み込み、step 7-3 以降 + Manus + Phase 3-5 を実行する。
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
from modules.contract_workflow import (
    ContractWorkBranch,
    resolve_contract_work_branch,
)
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
from modules.llm.llm_step_trace import (
    _step_seq,
    begin_case_llm_trace,
    end_case_llm_trace,
)
from modules.standard_cp_claude_manual import (
    CLAUDE_STANDARD_CP_MODEL,
    StandardCpManualClaudeOutputs,
    _build_site_build_prompt_from_steps,
    run_standard_cp_claude_api_call_14_of_16,
    run_standard_cp_claude_api_call_15_of_16,
    run_standard_cp_claude_api_call_16_of_16,
)
from main import WebsiteBot

logger = logging.getLogger("resume_step73")


def _read_file(record: str, step_num: int, kind: str, name: str) -> str:
    p = OUTPUT_DIR / record / "llm_steps" / f"{step_num:03d}_claude_cli_{kind}" / name
    if not p.is_file():
        logger.warning("ファイルなし: %s", p)
        return ""
    return p.read_text(encoding="utf-8")


def _out(record: str, step: int, kind: str) -> str:
    return _read_file(record, step, kind, "output.md")


def _inp(record: str, step: int, kind: str) -> str:
    return _read_file(record, step, kind, "input.md")


def resume_case(record_number: str) -> None:
    bot = WebsiteBot()
    case = bot.spreadsheet.get_case_by_record_number(record_number)
    if case is None:
        logger.error("レコード %s が見つかりません", record_number)
        sys.exit(1)

    logger.info(
        "再開: record=%s row=%s partner=%s",
        record_number, case["row_number"], case["partner_name"],
    )

    bot.spreadsheet.update_ai_status(case["row_number"], "MacBot")

    bundle = extract_hearing_bundle(
        case, fetch_hearing_sheet=bot.spec_generator.fetch_hearing_sheet,
    )

    # --- 保存済みステップ出力を StandardCpManualClaudeOutputs に復元 ---
    outs = StandardCpManualClaudeOutputs()
    outs.step_1_1 = _out(record_number, 1, "generate")
    outs.step_1_3 = _out(record_number, 2, "chat")
    outs.step_2 = _out(record_number, 3, "chat")
    outs.step_3_1 = _out(record_number, 4, "chat")
    outs.step_3_2 = _out(record_number, 5, "chat")
    outs.step_3_3 = _out(record_number, 6, "chat")
    outs.step_3_4 = _out(record_number, 7, "chat")
    outs.step_3_5 = _out(record_number, 8, "chat")
    outs.step_url_hearing = _out(record_number, 9, "generate")
    outs.step_url_appo = _out(record_number, 10, "generate")
    outs.step_4 = _out(record_number, 11, "chat")
    outs.step_5_assistant_ack = _out(record_number, 12, "chat")
    outs.step_6 = _out(record_number, 13, "chat")

    outs.raw = {
        "step_1_1": outs.step_1_1,
        "step_1_2": "",
        "step_1_3": outs.step_1_3,
        "step_2": outs.step_2,
        "step_3_1": outs.step_3_1,
        "step_3_2": outs.step_3_2,
        "step_3_3": outs.step_3_3,
        "step_3_4": outs.step_3_4,
        "step_3_5": outs.step_3_5,
        "step_4": outs.step_4,
        "step_5": outs.step_5_assistant_ack,
        "step_6": outs.step_6,
    }
    outs.raw_prompts = {
        "step_1_1": _inp(record_number, 1, "generate"),
        "step_1_2": _inp(record_number, 2, "chat"),
        "step_1_3": _inp(record_number, 2, "chat"),
        "step_2": _inp(record_number, 3, "chat"),
        "step_3_1": _inp(record_number, 4, "chat"),
        "step_3_2": _inp(record_number, 5, "chat"),
        "step_3_3": _inp(record_number, 6, "chat"),
        "step_3_4": _inp(record_number, 7, "chat"),
        "step_3_5": _inp(record_number, 8, "chat"),
        "step_4": _inp(record_number, 11, "chat"),
        "step_5": _inp(record_number, 12, "chat"),
        "step_6": _inp(record_number, 13, "chat"),
    }

    s71_prompt = _inp(record_number, 14, "chat")
    s71_response = _out(record_number, 14, "chat")
    s72_prompt = _inp(record_number, 15, "chat")
    s72_response = _out(record_number, 15, "chat")

    begin_case_llm_trace(record_number)
    _step_seq.set(15)

    batch1 = (
        "\n\n=== 手順3-2 サービスページ ===\n\n" + outs.step_3_2
        + "\n\n=== 手順3-3 会社概要 ===\n\n" + outs.step_3_3
    )
    batch2 = (
        "\n\n=== 手順3-4 お問い合わせ ===\n\n" + outs.step_3_4
        + "\n\n=== 手順3-5 その他 ===\n\n" + outs.step_3_5
    )

    hs = bundle.hearing_sheet_content
    am = bundle.appo_memo
    sn = bundle.sales_notes

    # --- step 7-3 (API 14/16・下層1群目) ---
    logger.info("手順7-3 を再開します（下層1群目・タイムアウト 1800s）…")
    p73, r73 = run_standard_cp_claude_api_call_14_of_16(
        step_7_1_prompt=s71_prompt,
        step_7_1_response=s71_response,
        step_7_2_prompt=s72_prompt,
        step_7_2_response=s72_response,
        step_3_lower_batch1=batch1,
        hearing_sheet_content=hs,
        appo_memo=am,
        sales_notes=sn,
    )
    outs.step_7_3 = r73
    outs.raw["step_7_3"] = r73
    outs.raw_prompts["step_7_3"] = p73

    # --- step 7-4 (API 15/16・下層2群目) ---
    logger.info("手順7-4 を実行します（下層2群目）…")
    p74, r74 = run_standard_cp_claude_api_call_15_of_16(
        step_7_1_prompt=s71_prompt,
        step_7_1_response=s71_response,
        step_7_2_prompt=s72_prompt,
        step_7_2_response=s72_response,
        step_7_3_prompt=p73,
        step_7_3_response=r73,
        step_3_lower_batch2=batch2,
        hearing_sheet_content=hs,
        appo_memo=am,
        sales_notes=sn,
    )
    outs.step_7_4 = r74
    outs.raw["step_7_4"] = r74
    outs.raw_prompts["step_7_4"] = p74

    # --- step 7-5 (API 16/16・最終仕上げ) ---
    logger.info("手順7-5 を実行します（最終仕上げ）…")
    p75, r75 = run_standard_cp_claude_api_call_16_of_16(
        step_7_1_prompt=s71_prompt,
        step_7_1_response=s71_response,
        step_7_2_prompt=s72_prompt,
        step_7_2_response=s72_response,
        step_7_3_prompt=p73,
        step_7_3_response=r73,
        step_7_4_prompt=p74,
        step_7_4_response=r74,
    )
    outs.step_7_5 = r75
    outs.raw["step_7_5"] = r75
    outs.raw_prompts["step_7_5"] = p75
    outs.step_7_1 = s71_response
    outs.step_7_2 = s72_response

    canvas_final = (r75 or "").strip() or r74

    # --- Manus リファクタ ---
    manus_deploy_github_url: str | None = None
    if STANDARD_CP_REFACTOR_AFTER_MANUAL:
        from modules.claude_manual_common import run_manus_refactor_block

        extras = [s for s in (am, sn) if (s or "").strip()]
        hr = hearing_reference_design_block_for_prompt(hs, extra_texts=extras)
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
            hearing_reference_block=hr,
            contract_max_pages=max_pages,
            preface_dir=STANDARD_CP_REFACTOR_PREFACE_DIR,
        )
        outs.raw_prompts["manus_refactor_task"] = _prompt
        outs.step_refactor = md
        outs.raw["step_refactor"] = md
        outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    # --- spec 組み立て ---
    combined = _build_site_build_prompt_from_steps(
        outs,
        partner_name=case["partner_name"],
        hearing_sheet_content=hs,
        appo_memo=am,
        sales_notes=sn,
    )
    plan_info = get_contract_plan_info((case.get("contract_plan") or "").strip())
    max_pages = int(plan_info.get("pages") or 6)

    if len(combined.strip()) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            f"結合要望テキストが短すぎます（{len(combined)} / 最低 {MIN_SITE_BUILD_PROMPT_CHARS}）"
        )

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
    bot._phase5_deploy(case, spec, site_dir)
    logger.info("再開完了: record=%s", record_number)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/_resume_from_step73.py <record_number>")
        sys.exit(1)
    resume_case(sys.argv[1])
