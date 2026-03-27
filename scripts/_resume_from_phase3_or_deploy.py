"""中断した案件を Phase 3（shallow clone）または Phase 5（デプロイ）から再開する。

使い方:
    RESUME_RECORD=16308 python scripts/_resume_from_phase3_or_deploy.py

site_dir の状態を自動判定:
  - package.json がない → Manus GitHub から shallow clone → build → deploy
  - package.json あり    → deploy のみ
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.logging_setup import configure_logging

configure_logging()

import yaml

from config.config import (
    GA4_INJECT_TRACKING,
    GA4_MEASUREMENT_ID,
    OUTPUT_DIR,
    get_contract_plan_info,
)
from modules.contract_workflow import resolve_contract_work_branch
from modules.ga4_injector import inject_ga4_tracking
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_manus_only_style_run_artifacts,
)
from main import WebsiteBot

logger = logging.getLogger("resume_phase")


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _find_site_dir(record_number: str) -> Path | None:
    sites = OUTPUT_DIR / "sites"
    if not sites.is_dir():
        return None
    for d in sites.iterdir():
        if d.is_dir() and d.name.endswith(f"-{record_number}"):
            return d
    return None


def run() -> None:
    record_number = os.environ.get("RESUME_RECORD", "").strip()
    if not record_number:
        logger.error("RESUME_RECORD 環境変数を設定してください")
        sys.exit(1)

    bot = WebsiteBot()
    case = bot.spreadsheet.get_case_by_record_number(record_number)
    if case is None:
        logger.error("レコード %s がスプレッドシートに見つかりません", record_number)
        sys.exit(1)

    logger.info(
        "案件取得: record=%s row=%s partner=%s plan=%s",
        record_number, case["row_number"], case["partner_name"], case["contract_plan"],
    )

    plan_raw = (case.get("contract_plan") or "").strip()
    plan_info = get_contract_plan_info(plan_raw)
    work_branch = resolve_contract_work_branch(plan_raw)

    site_dir = _find_site_dir(record_number)
    if site_dir is None:
        site_name = f"{case['partner_name']}-{record_number}"
        site_dir = OUTPUT_DIR / "sites" / site_name
        site_dir.mkdir(parents=True, exist_ok=True)

    llm_raw_dir = site_dir / "llm_raw_output"
    manus_url_file = llm_raw_dir / "manus_deploy_github_url.txt"
    manus_github_url = ""
    if manus_url_file.is_file():
        manus_github_url = manus_url_file.read_text(encoding="utf-8").strip()

    spec_path = llm_raw_dir / "spec.yaml"
    req_path = llm_raw_dir / "requirements_result.yaml"
    spec: dict = _load_yaml(spec_path) if spec_path.is_file() else {}
    req: dict = _load_yaml(req_path) if req_path.is_file() else {}

    if manus_github_url:
        spec["manus_deploy_github_url"] = manus_github_url
    logger.info("manus_deploy_github_url=%s", spec.get("manus_deploy_github_url", "(なし)"))

    pkg = site_dir / "package.json"
    if pkg.is_file():
        # ---- ビルド済み → Phase 5 のみ ----
        # Manus の GitHub リポが 404 の場合はローカルから push するため URL をクリア
        force_local_push = os.environ.get("FORCE_LOCAL_PUSH", "").strip().lower() in ("1", "true", "yes")
        if force_local_push and "manus_deploy_github_url" in spec:
            logger.info("FORCE_LOCAL_PUSH=true → manus_deploy_github_url をクリアしてローカル push")
            del spec["manus_deploy_github_url"]
        logger.info("package.json あり → Phase 5（デプロイ）のみ実行")
        deploy_url = bot._phase5_deploy(case, spec, site_dir)
        logger.info("完了！デプロイ URL: %s", deploy_url)
        return

    # ---- package.json なし → Phase 3 から ----
    logger.info("package.json なし → Phase 3（shallow clone）から再開")

    if not manus_github_url:
        logger.error("manus_deploy_github_url がないため shallow clone できません")
        sys.exit(1)

    llm_raw_backup = None
    if llm_raw_dir.is_dir():
        llm_raw_backup = Path(str(llm_raw_dir) + "_backup")
        if llm_raw_backup.exists():
            shutil.rmtree(llm_raw_backup)
        shutil.copytree(llm_raw_dir, llm_raw_backup)
        logger.info("llm_raw_output をバックアップ: %s", llm_raw_backup)

    for item in site_dir.iterdir():
        if item.name in ("llm_raw_output", "llm_raw_output_backup"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    logger.info("Manus GitHub から shallow clone…")
    bot.github_client.shallow_clone_repo_into_site_dir(manus_github_url, site_dir)

    if llm_raw_backup and llm_raw_backup.is_dir():
        dst = site_dir / "llm_raw_output"
        if not dst.is_dir():
            shutil.copytree(llm_raw_backup, dst)
        shutil.rmtree(llm_raw_backup, ignore_errors=True)

    raw_n = write_llm_raw_artifacts(
        site_dir, spec=spec, requirements_result=req, work_branch=work_branch,
    )
    logger.info("LLM 正本: llm_raw_output/ に %s ファイル", raw_n)

    manus_snap = write_manus_only_style_run_artifacts(
        site_dir, spec=spec, work_branch=work_branch,
        partner_name=str(case.get("partner_name") or ""),
        record_number=record_number,
    )
    if manus_snap is not None:
        logger.info("Manus 工程テスト互換: %s", manus_snap.relative_to(site_dir.resolve()))

    if GA4_INJECT_TRACKING:
        inject_ga4_tracking(site_dir, measurement_id=GA4_MEASUREMENT_ID)

    logger.info("【Phase 4】ビルド検証…")
    bot._phase4_build(case, spec, site_dir, work_branch, plan_info)

    logger.info("【Phase 5】デプロイ…")
    deploy_url = bot._phase5_deploy(case, spec, site_dir)
    logger.info("完了！デプロイ URL: %s", deploy_url)


if __name__ == "__main__":
    run()
