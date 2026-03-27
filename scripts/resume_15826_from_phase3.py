"""案件15826: Manus GitHub repo から shallow clone して Phase 3-5 を再実行。

Phase 2 は完了済み。Manus が GitHub に push した完全なリポジトリを使い、
site_dir を再構築して build→deploy まで通す。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.logging_setup import configure_logging

configure_logging()

import logging
import shutil
import yaml

from config.config import OUTPUT_DIR, get_contract_plan_info
from modules.contract_workflow import (
    ContractWorkBranch,
    resolve_contract_work_branch,
)
from modules.github_client import GitHubClient
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_manus_only_style_run_artifacts,
)
from main import WebsiteBot

logger = logging.getLogger("resume_15826")

RECORD_NUMBER = "15826"
SITE_NAME = "株式会社ReVALUE-15826"
MANUS_GITHUB_URL = "https://github.com/propagate-webcreation/15826-ReVALUE.git"

PHASE2_RAW = (
    OUTPUT_DIR / "phase2_complete" / SITE_NAME / "llm_raw_output"
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def run() -> None:
    bot = WebsiteBot()

    case = bot.spreadsheet.get_case_by_record_number(RECORD_NUMBER)
    if case is None:
        logger.error("レコード %s がスプレッドシートに見つかりません", RECORD_NUMBER)
        sys.exit(1)

    logger.info(
        "案件取得: record=%s row=%s partner=%s plan=%s",
        RECORD_NUMBER,
        case["row_number"],
        case["partner_name"],
        case["contract_plan"],
    )

    plan_raw = (case.get("contract_plan") or "").strip()
    plan_info = get_contract_plan_info(plan_raw)
    work_branch = resolve_contract_work_branch(plan_raw)

    # --- Phase 2 の成果物を復元 ---
    spec_path = PHASE2_RAW / "spec.yaml"
    req_path = PHASE2_RAW / "requirements_result.yaml"
    if not spec_path.is_file() or not req_path.is_file():
        logger.error("Phase 2 の成果物が見つかりません: %s", PHASE2_RAW)
        sys.exit(1)

    spec = _load_yaml(spec_path)
    req = _load_yaml(req_path)

    spec["manus_deploy_github_url"] = MANUS_GITHUB_URL
    logger.info("spec 復元: keys=%s", list(spec.keys()))
    logger.info("manus_deploy_github_url=%s", MANUS_GITHUB_URL)

    # --- site_dir を再構築 ---
    site_dir = OUTPUT_DIR / "sites" / SITE_NAME
    llm_raw_backup = None

    if site_dir.is_dir():
        llm_raw = site_dir / "llm_raw_output"
        if llm_raw.is_dir():
            llm_raw_backup = Path(str(llm_raw) + "_backup")
            if llm_raw_backup.exists():
                shutil.rmtree(llm_raw_backup)
            shutil.copytree(llm_raw, llm_raw_backup)
            logger.info("llm_raw_output をバックアップ: %s", llm_raw_backup)

        for item in site_dir.iterdir():
            if item.name in ("llm_raw_output", "llm_raw_output_backup"):
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        logger.info("site_dir をクリーン: %s", site_dir)
    else:
        site_dir.mkdir(parents=True, exist_ok=True)

    # --- Manus GitHub repo から shallow clone ---
    logger.info("Manus GitHub から shallow clone…")
    bot.github_client.shallow_clone_repo_into_site_dir(MANUS_GITHUB_URL, site_dir)

    if llm_raw_backup and llm_raw_backup.is_dir():
        dst = site_dir / "llm_raw_output"
        if not dst.is_dir():
            shutil.copytree(llm_raw_backup, dst)
        shutil.rmtree(llm_raw_backup, ignore_errors=True)
        logger.info("llm_raw_output を復元")

    pkg = site_dir / "package.json"
    logger.info("package.json 存在: %s", pkg.is_file())

    # --- LLM raw output 保存 ---
    raw_n = write_llm_raw_artifacts(
        site_dir, spec=spec, requirements_result=req, work_branch=work_branch,
    )
    logger.info("LLM 正本: llm_raw_output/ に %s ファイル", raw_n)

    manus_snap = write_manus_only_style_run_artifacts(
        site_dir,
        spec=spec,
        work_branch=work_branch,
        partner_name=str(case.get("partner_name") or ""),
        record_number=RECORD_NUMBER,
    )
    if manus_snap is not None:
        logger.info("Manus 工程テスト互換: %s", manus_snap.relative_to(site_dir.resolve()))

    from modules.ga4_injector import inject_ga4_tracking
    from config.config import GA4_INJECT_TRACKING, GA4_MEASUREMENT_ID
    if GA4_INJECT_TRACKING:
        inject_ga4_tracking(site_dir, measurement_id=GA4_MEASUREMENT_ID)

    # --- Phase 4: ビルド ---
    logger.info("【Phase 4】ビルド検証…")
    bot._phase4_build(case, spec, site_dir, work_branch, plan_info)

    # --- Phase 5: デプロイ ---
    logger.info("【Phase 5】デプロイ…")
    deploy_url = bot._phase5_deploy(case, spec, site_dir)

    logger.info("完了！デプロイ URL: %s", deploy_url)


if __name__ == "__main__":
    run()
