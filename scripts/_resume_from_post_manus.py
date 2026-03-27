"""Manus 完了済み案件の post-Manus 検証 → Phase 3-5 再開スクリプト。

保存済み llm_steps/019_manus_refactor/output.md を使い、
新しい post-Manus 検証エージェントで URL を再判定してから Phase 3-5 を実行する。

Usage:
    python scripts/_resume_from_post_manus.py <record_number> [record_number2 ...]
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
    get_contract_plan_info,
)
from modules.basic_lp_refactor_claude import (
    STANDARD_CP_REFACTOR_PREFACE_DIR,
    _verify_manus_response_via_claude_cli,
    _verify_github_url_reachable,
)
from modules.case_extraction import extract_hearing_bundle
from modules.contract_workflow import ContractWorkBranch, resolve_contract_work_branch
from modules.github_client import sanitize_github_repo_name
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
from modules.standard_cp_claude_manual import (
    CLAUDE_STANDARD_CP_MODEL,
    StandardCpManualClaudeOutputs,
    _build_site_build_prompt_from_steps,
)
from main import WebsiteBot

logger = logging.getLogger("resume_post_manus")


def _read_step(record: str, step_num: int, kind: str, name: str) -> str:
    p = OUTPUT_DIR / record / "llm_steps" / f"{step_num:03d}_claude_cli_{kind}" / name
    if not p.is_file():
        p2 = OUTPUT_DIR / record / "llm_steps" / f"{step_num:03d}_manus_refactor" / name
        if p2.is_file():
            return p2.read_text(encoding="utf-8")
        return ""
    return p.read_text(encoding="utf-8")


def _out(record: str, step: int, kind: str) -> str:
    return _read_step(record, step, kind, "output.md")


def _inp(record: str, step: int, kind: str) -> str:
    return _read_step(record, step, kind, "input.md")


def resume_post_manus(record_number: str) -> None:
    manus_output_path = OUTPUT_DIR / record_number / "llm_steps" / "019_manus_refactor" / "output.md"
    if not manus_output_path.is_file():
        logger.error("Manus 出力が見つかりません: %s", manus_output_path)
        sys.exit(1)

    manus_response = manus_output_path.read_text(encoding="utf-8")
    logger.info("Manus 保存済み応答を読み込み: %d chars", len(manus_response))

    bot = WebsiteBot()
    case = bot.spreadsheet.get_case_by_record_number(record_number)
    if case is None:
        logger.error("レコード %s が見つかりません", record_number)
        sys.exit(1)

    partner_name = case["partner_name"]
    contract_plan = (case.get("contract_plan") or "").strip()
    logger.info("再開: record=%s partner=%s plan=%s", record_number, partner_name, contract_plan)
    bot.spreadsheet.update_ai_status(case["row_number"], "MacBot")

    bundle = extract_hearing_bundle(
        case, fetch_hearing_sheet=bot.spec_generator.fetch_hearing_sheet,
    )
    hs = bundle.hearing_sheet_content
    am = bundle.appo_memo
    sn = bundle.sales_notes

    # --- 保存済み Claude CLI 出力を復元 ---
    outs = StandardCpManualClaudeOutputs()
    step_map = {
        1: ("generate", "step_1_1"),
        2: ("chat", "step_1_3"),
        3: ("chat", "step_2"),
        4: ("chat", "step_3_1"),
        5: ("chat", "step_3_2"),
        6: ("chat", "step_3_3"),
        7: ("chat", "step_3_4"),
        8: ("chat", "step_3_5"),
        11: ("chat", "step_4"),
        12: ("chat", "step_5"),
        13: ("chat", "step_6"),
        14: ("chat", "step_7_1"),
        15: ("chat", "step_7_2"),
        16: ("chat", "step_7_3"),
        17: ("chat", "step_7_4"),
        18: ("chat", "step_7_5"),
    }
    for step_num, (kind, key) in step_map.items():
        val = _out(record_number, step_num, kind)
        if val:
            setattr(outs, key, val)
            outs.raw[key] = val
            outs.raw_prompts[key] = _inp(record_number, step_num, kind)

    outs.raw["step_1_2"] = ""
    outs.raw_prompts["step_1_2"] = outs.raw_prompts.get("step_1_3", "")

    canvas_final = (outs.step_7_5 or "").strip() or outs.step_7_4

    # --- post-Manus 検証（新ロジック）---
    expected_repo = sanitize_github_repo_name(partner_name, record_number)
    result = _verify_manus_response_via_claude_cli(
        manus_response,
        record_number=record_number,
        partner_name=partner_name,
        expected_repo_name=expected_repo,
        model=CLAUDE_STANDARD_CP_MODEL,
    )
    logger.info("post-Manus 検証結果: %s", result)

    manus_deploy_github_url: str | None = None
    candidate = result.github_url
    if result.recovery == "USE_EXISTING_REPO" and not candidate:
        candidate = result.recovery_url
    if candidate and _verify_github_url_reachable(candidate):
        manus_deploy_github_url = candidate
        logger.info("deploy URL 確定: %s", manus_deploy_github_url)
    elif candidate:
        logger.warning("URL が git ls-remote で到達不可: %s", candidate)

    outs.step_refactor = manus_response
    outs.raw["step_refactor"] = manus_response
    outs.raw["step_refactor_deploy_github_url"] = manus_deploy_github_url or ""

    # --- spec 組み立て ---
    combined = _build_site_build_prompt_from_steps(
        outs, partner_name=partner_name,
        hearing_sheet_content=hs, appo_memo=am, sales_notes=sn,
    )
    plan_info = get_contract_plan_info(contract_plan)
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
        req, contract_plan, partner_name,
    )
    spec["standard_manual_claude_final"] = canvas_final
    spec["standard_refactored_source_markdown"] = outs.step_refactor or ""
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()
    spec["standard_manual_claude_step_2"] = outs.step_2
    spec["standard_manual_claude_step_6"] = outs.step_6

    site_name = f"{partner_name}-{record_number}"
    write_llm_raw_artifacts_phase2_snapshot(
        site_name=site_name, spec=spec, requirements_result=req,
        work_branch=ContractWorkBranch.STANDARD,
    )

    # --- Phase 3-5 ---
    work_branch = resolve_contract_work_branch(contract_plan)
    site_dir = bot._phase3_prepare_site(case, req, spec, work_branch)
    bot._phase4_build(case, spec, site_dir, work_branch, plan_info)
    deploy_url = bot._phase5_deploy(case, spec, site_dir)
    logger.info("再開完了: record=%s deploy=%s", record_number, deploy_url)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/_resume_from_post_manus.py <record_number> [...]")
        sys.exit(1)
    for rec in sys.argv[1:]:
        resume_post_manus(rec)
