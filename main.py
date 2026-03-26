"""メインオーケストレーション

完成サイトを GitHub に push し Vercel で公開するまでを一本化する。

パイプライン概略:
  1. ヒアリングシート類の抽出（`modules.case_extraction`）
  2. TEXT_LLM（`modules.llm.text_llm_stage` — プランは ``if/elif`` で分岐。各 ``*_USE_CLAUDE_MANUAL`` と Claude CLI の認証が必要）
  3. 出力先ディレクトリ準備（テンプレコピーなし）→ `llm_raw_output/` に LLM 生出力を保存
     （Manus 待ちで 3 に進めない間は `output/phase2_llm_checkpoints/…/pre_manus/` に TEXT_LLM（Claude CLI）分のみ先行保存）
  4. フェンス解析で TEXT_LLM 出力のみ `app/` 等へ反映（失敗時は例外）
  5. ビルド検証（失敗時も成果物の自動修正は行わない）
  6. GitHub push → Vercel デプロイ → site-annotator 登録 → スプレッドシートに公開 URL

各段の LLM 割当は ``docs/LLM_PIPELINE.md`` を参照。
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from config.logging_setup import configure_logging

# 他 import より先にログ設定（import 時のログレベルが揃う）
configure_logging()

from config.config import (
    BOT_MAX_CASES,
    BOT_ONLY_RECORD_NUMBER,
    BOT_RESUME_FROM_MANUS,
    OUTPUT_DIR,
    SITE_BUILD_ENABLED,
    SITE_IMPLEMENTATION_ENABLED,
    SITE_PROVISION_API_KEY,
    SITE_PROVISION_API_URL,
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN,
    SPREADSHEET_HEADERS_STRICT,
    get_contract_plan_info,
)
from config.log_theme import (
    all_done_banner,
    batch_start_banner,
    case_start_banner,
    idle_banner,
    startup_title,
    stream_supports_color,
)
from config.types import CaseRecord
from config.validation import StartupValidationResult, validate_startup_config
from modules.basic_lp_generated_apply import apply_contract_outputs_to_site_dir
from modules.case_extraction import extract_hearing_bundle
from modules.contract_workflow import (
    BRANCH_REGISTRY,
    ContractWorkBranch,
    claude_manual_enabled_for_branch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)
from modules.github_client import GitHubClient, sanitize_github_repo_name
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_llm_raw_artifacts_phase2_snapshot,
    write_manus_only_style_run_artifacts,
)
from modules.llm.llm_step_trace import begin_case_llm_trace, end_case_llm_trace
from modules.llm.text_llm_stage import run_text_llm_stage
from modules.site_build import verify_site_build
from modules.site_generator import SiteGenerator
from modules.site_implementer import SiteImplementer
from modules.spec_generator import SpecGenerator
from modules.spreadsheet import (
    SpreadsheetClient,
    ai_cell_excludes_from_pending_queue,
    missing_required_case_fields,
)
from modules.vercel_client import (
    VercelClient,
    github_owner_repo_from_clone_url,
    sanitize_vercel_project_name,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Manus 再開モード: 保存済み Canvas から Claude マニュアル段をスキップして Manus 以降を実行
# ---------------------------------------------------------------------------



def _resume_from_manus(
    *,
    record_number: str,
    partner_name: str,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    work_branch: ContractWorkBranch,
    contract_max_pages: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """保存済み Claude Canvas を読み込み、Manus リファクタ以降のみ実行して spec を返す。

    引数: record_number（出力ディレクトリの特定）/ hearing 情報（Manus プロンプト内の参考ブロック用）
          / work_branch・contract_max_pages（プラン別制御）
    処理: output/{record}/llm_steps/011_claude_cli_chat/output.md を読み、
          run_basic_lp_refactor_stage で Manus のみ実行
    出力: (requirements_result, spec) — process_case のフェーズ3 以降が使う最低限のキーを格納
    """
    from modules.basic_lp_refactor_claude import run_basic_lp_refactor_stage
    from modules.hearing_url_utils import hearing_reference_design_block_for_prompt

    trace_dir = OUTPUT_DIR / record_number / "llm_steps" / "011_claude_cli_chat"
    canvas_path = trace_dir / "output.md"
    if not canvas_path.is_file():
        raise FileNotFoundError(
            f"Claude マニュアル最終出力が見つかりません（Manus 再開には前回の TEXT_LLM（Claude CLI）完走が必要）: {canvas_path}"
        )
    canvas = canvas_path.read_text(encoding="utf-8")
    logger.info(
        "Manus 再開: 保存済み Canvas を読み込みました (%s chars) path=%s",
        len(canvas), canvas_path,
    )

    extras = [s for s in (appo_memo, sales_notes) if (s or "").strip()]
    hr = hearing_reference_design_block_for_prompt(hearing_sheet_content, extra_texts=extras)

    md, manus_deploy_github_url = run_basic_lp_refactor_stage(
        canvas_source_code=canvas,
        partner_name=partner_name,
        record_number=record_number,
        hearing_reference_block=hr,
        contract_max_pages=contract_max_pages,
    )

    refactor_key, canvas_key = BRANCH_REGISTRY[work_branch].manus_keys
    requirements_result: dict[str, Any] = {
        "plan_type": work_branch.value,
        "site_build_prompt": f"[Manus再開] Canvas {len(canvas)} chars → refactor {len(md)} chars",
    }
    spec: dict[str, Any] = {
        canvas_key: canvas,
        refactor_key: md,
    }
    if manus_deploy_github_url:
        spec["manus_deploy_github_url"] = manus_deploy_github_url.strip()

    return requirements_result, spec


# ---------------------------------------------------------------------------
# スプレッドシート R 列用のエラー文言短縮（セル幅・可読性のため）
# ---------------------------------------------------------------------------


def _format_ai_status_error(exc: BaseException) -> str:
    """R 列向けに例外メッセージを短く整形（モジュールパス連呼を削る）。"""
    msg = (str(exc) or type(exc).__name__).strip()
    for noise in (
        "（modules.spec_generator）。",
        " modules.spec_generator",
        " modules.llm.llm_pipeline_common",
        "（modules.llm.llm_pipeline_common）。",
        "（modules.llm.llm_pipeline_common.finalize_plain_prompt）。",
        "（modules.llm.llm_pipeline_common.assemble_spec_dict_from_requirements）。",
        " modules.llm.text_llm_stage",
        "（modules.llm.text_llm_stage）。",
        " modules.llm.basic_lp_spec",
        "（modules.llm.basic_lp_spec）。",
        " modules.llm.basic_cp_spec",
        "（modules.llm.basic_cp_spec）。",
        " modules.basic_lp_claude_manual",
        "（modules.basic_lp_claude_manual）。",
        " modules.basic_cp_claude_manual",
        "（modules.basic_cp_claude_manual）。",
        " modules.standard_cp_claude_manual",
        "（modules.standard_cp_claude_manual）。",
        " modules.advance_cp_claude_manual",
        "（modules.advance_cp_claude_manual）。",
        " modules.basic_lp_generated_apply",
        "（modules.basic_lp_generated_apply）。",
        " modules.case_extraction",
        "（modules.case_extraction）。",
    ):
        msg = msg.replace(noise, "")
    msg = " ".join(msg.split())
    prefix = "エラー: "
    budget = max(24, SPREADSHEET_AI_STATUS_ERROR_MAX_LEN - len(prefix))
    if len(msg) > budget:
        msg = msg[: budget - 1] + "…"
    return prefix + msg


# ---------------------------------------------------------------------------
# ボット本体: 1 バッチ = 複数案件を run() で列挙し、各案件は process_case()
# ---------------------------------------------------------------------------


class WebsiteBot:
    """Webサイト製作自動化Bot"""

    def __init__(self) -> None:
        """SpreadsheetClient を常に初期化する。"""
        self.spreadsheet = SpreadsheetClient()
        self.spec_generator = SpecGenerator()
        self.site_implementer = SiteImplementer()
        self.site_generator = SiteGenerator()
        self._github_client: GitHubClient | None = None
        self.vercel_client = VercelClient()

    @property
    def github_client(self) -> GitHubClient:
        """GitHub push 直前まで初期化しない（起動時の設定検証を軽くする）。"""
        if self._github_client is None:
            self._github_client = GitHubClient()
        return self._github_client

    # ------------------------------------------------------------------
    # process_case: 5 フェーズを順に実行するオーケストレーション
    # ------------------------------------------------------------------

    def process_case(self, case: CaseRecord) -> str | None:
        """案件を処理。デプロイ URL（成功時）、着手しない場合は None を返す。"""
        missing = missing_required_case_fields(case)
        if missing:
            logger.error(
                "必須項目が未入力のため案件に着手しません row=%s missing=%s",
                case.get("row_number"), missing,
            )
            return None

        self.spreadsheet.update_ai_status(case["row_number"], "MacBot")
        logger.info(case_start_banner(
            row=case.get("row_number"),
            record=case.get("record_number"),
            partner=case.get("partner_name"),
            use_color=stream_supports_color(sys.stdout),
        ))
        trace_root = begin_case_llm_trace(str(case.get("record_number") or ""))
        logger.info("LLM 入出力トレース: %s/llm_steps/", trace_root)
        try:
            try:
                result = self._phase1_hearing_and_branch(case)
                if result is None:
                    return None
                bundle, work_branch, plan_info = result

                req, spec = self._phase2_text_llm(case, bundle, work_branch, plan_info)
                site_dir = self._phase3_prepare_site(case, req, spec, work_branch)
                self._phase4_build(case, spec, site_dir, work_branch, plan_info)
                return self._phase5_deploy(case, spec, site_dir)
            finally:
                end_case_llm_trace()
        except Exception as e:
            logger.error(
                "案件処理エラー row=%s record=%s partner=%s: %s",
                case.get("row_number"), case.get("record_number"),
                case.get("partner_name"), e, exc_info=True,
            )
            try:
                self.spreadsheet.update_ai_status(
                    case["row_number"], _format_ai_status_error(e),
                )
            except Exception as sheet_err:
                logger.warning(
                    "エラー後のスプレッドシートステータス更新に失敗 row=%s: %s",
                    case.get("row_number"), sheet_err, exc_info=True,
                )
            raise

    # ------------------------------------------------------------------
    # フェーズ1: ヒアリング抽出 + 作業分岐の解決
    # ------------------------------------------------------------------

    def _phase1_hearing_and_branch(
        self, case: CaseRecord,
    ) -> tuple[Any, ContractWorkBranch, dict[str, Any]] | None:
        """引数: case（スプレッドシート行）
        処理: ヒアリング本文・メモ抽出 → 契約プラン列から作業分岐を解決
        出力: (hearing_bundle, work_branch, plan_info)。ヒアリング空ならスキップで None。
        """

        logger.info("【フェーズ1】ヒアリングシート類の抽出…")
        hearing_bundle = extract_hearing_bundle(
            case, fetch_hearing_sheet=self.spec_generator.fetch_hearing_sheet,
        )
        if not (hearing_bundle.hearing_sheet_content or "").strip():
            logger.warning(
                "ヒアリング本文が空のため案件をスキップします row=%s record=%s partner=%s",
                case.get("row_number"), case.get("record_number"),
                case.get("partner_name"),
            )
            self.spreadsheet.update_ai_status(
                case["row_number"], "スキップ: ヒアリング本文なし（AH列の取得結果が空）",
            )
            return None

        plan_raw = (case.get("contract_plan") or "").strip()
        plan_info = get_contract_plan_info(plan_raw)
        work_branch_before_lp = resolve_contract_work_branch(case["contract_plan"])
        work_branch = resolve_work_branch_with_basic_lp_override(
            case["contract_plan"],
            record_number=str(case.get("record_number") or ""),
            partner_name=str(case.get("partner_name") or ""),
            lookup_basic_is_landing_page=self.spreadsheet.lookup_basic_is_landing_page,
        )
        if (
            work_branch_before_lp == ContractWorkBranch.BASIC
            and work_branch == ContractWorkBranch.BASIC_LP
        ):
            logger.info(
                "BASIC サイトタイプシートにより作業分岐を BASIC LP に変更しました (record=%r)",
                case.get("record_number"),
            )
        logger.info(
            "契約プラン作業分岐: plan=%r branch=%s plan_column_type=%s plan_column_pages=%s",
            plan_raw, work_branch.value, plan_info.get("type"), plan_info.get("pages"),
        )
        return hearing_bundle, work_branch, plan_info

    # ------------------------------------------------------------------
    # フェーズ2: TEXT_LLM（Claude CLI マニュアルチェーン or Manus 再開）
    # ------------------------------------------------------------------

    def _phase2_text_llm(
        self,
        case: CaseRecord,
        bundle: Any,
        work_branch: ContractWorkBranch,
        plan_info: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """引数: bundle（フェーズ1 出力）/ work_branch・plan_info（プラン制御）
        処理: BRANCH_REGISTRY でパイプライン選択。BOT_RESUME_FROM_MANUS 時は Manus のみ再実行
        出力: (requirements_result, spec)
        """
        if BOT_RESUME_FROM_MANUS:
            logger.info("【フェーズ2・Manus再開】Claude マニュアル段スキップ → Manus のみ実行 branch=%s", work_branch.value)
            req, spec = _resume_from_manus(
                record_number=str(case.get("record_number") or ""),
                partner_name=case["partner_name"],
                hearing_sheet_content=bundle.hearing_sheet_content,
                appo_memo=bundle.appo_memo,
                sales_notes=bundle.sales_notes,
                work_branch=work_branch,
                contract_max_pages=int(plan_info.get("pages") or 1),
            )
        else:
            logger.info("【フェーズ2】TEXT_LLM … branch=%s", work_branch.value)
            req, spec = run_text_llm_stage(
                bundle,
                contract_plan=case["contract_plan"],
                partner_name=case["partner_name"],
                record_number=str(case.get("record_number") or ""),
                work_branch=work_branch,
            )

        site_name = f"{case['partner_name']}-{case['record_number']}"
        write_llm_raw_artifacts_phase2_snapshot(
            site_name=site_name, spec=spec, requirements_result=req,
            work_branch=work_branch,
        )
        return req, spec

    # ------------------------------------------------------------------
    # フェーズ3: サイト出力先の準備・LLM 正本保存・フェンス適用
    # ------------------------------------------------------------------

    def _phase3_prepare_site(
        self,
        case: CaseRecord,
        requirements_result: dict[str, Any],
        spec: dict[str, Any],
        work_branch: ContractWorkBranch,
    ) -> Path:
        """引数: spec / requirements（フェーズ2 出力）/ work_branch
        処理: output/sites/ にディレクトリ生成 → llm_raw_output 書き出し → フェンス適用 → フォールバック clone
        出力: site_dir（ビルド・デプロイ可能な状態）
        """
        logger.info("【フェーズ3】出力先準備・LLM 正本の保存・フェンス適用…")
        site_name = f"{case['partner_name']}-{case['record_number']}"
        site_dir = self.site_generator.generate_site(spec, [], site_name)

        raw_n = write_llm_raw_artifacts(
            site_dir, spec=spec, requirements_result=requirements_result,
            work_branch=work_branch,
        )
        manus_snap = write_manus_only_style_run_artifacts(
            site_dir, spec=spec, work_branch=work_branch,
            partner_name=str(case.get("partner_name") or ""),
            record_number=str(case.get("record_number") or ""),
        )
        if manus_snap is not None:
            logger.info("› Manus 工程テスト互換: %s", manus_snap.relative_to(site_dir.resolve()))
        logger.info("› LLM 正本: llm_raw_output/ に %s ファイル", raw_n)

        manus_git_for_fallback = (spec.get("manus_deploy_github_url") or "").strip()

        n_gen = apply_contract_outputs_to_site_dir(spec, site_dir, work_branch=work_branch)
        if n_gen:
            logger.info("› フェンス解析でサイトに %s ファイル反映（分岐 %s）", n_gen, work_branch.value)

        if (
            work_branch in BRANCH_REGISTRY
            and n_gen == 0
            and (claude_manual_enabled_for_branch(work_branch) or manus_git_for_fallback)
        ):
            if manus_git_for_fallback:
                logger.warning(
                    "フェンスからファイル 0 件だが manus_deploy_github_url があるため "
                    "GitHub を shallow clone して続行します: %s", manus_git_for_fallback,
                )
                self.github_client.shallow_clone_repo_into_site_dir(manus_git_for_fallback, site_dir)
            else:
                raise RuntimeError(
                    "生成マークダウンからサイトファイルを1件も適用できませんでした。"
                    " 該当プランの Claude マニュアルとリファクタ出力が spec に入っているか確認してください。"
                )
        return site_dir

    # ------------------------------------------------------------------
    # フェーズ4: ビルド検証
    # ------------------------------------------------------------------

    def _phase4_build(
        self,
        case: CaseRecord,
        spec: dict[str, Any],
        site_dir: Path,
        work_branch: ContractWorkBranch,
        plan_info: dict[str, Any],
    ) -> None:
        """引数: site_dir（フェーズ3 出力）/ spec・plan_info（プラン制御）
        処理: package.json 存在確認 → npm build or 実装検証
        出力: なし（失敗時は RuntimeError）
        """
        if SITE_BUILD_ENABLED or SITE_IMPLEMENTATION_ENABLED:
            pkg = site_dir / "package.json"
            if not pkg.is_file():
                raise RuntimeError(
                    "package.json がありません。出力に `package.json` を含めてください。"
                )

        if SITE_IMPLEMENTATION_ENABLED:
            logger.info("› サイト実装を実行（npm build 検証）…")
            ok_impl, impl_log = self.site_implementer.implement(
                spec, site_dir, case["contract_plan"], work_branch=work_branch,
            )
            if not ok_impl:
                raise RuntimeError(
                    "サイト実装または npm build に失敗しました。ログ末尾: "
                    + (impl_log[-2000:] if impl_log else "")
                )
        elif SITE_BUILD_ENABLED:
            logger.info("› 実装はスキップ — npm build で検証のみ…")
            _cap = int(plan_info.get("pages") or 1)
            ok_b, blog = verify_site_build(site_dir, contract_max_pages=_cap)
            blog = blog or ""
            if not ok_b:
                raise RuntimeError("npm build に失敗: " + (blog[-2000:] if blog else ""))

    # ------------------------------------------------------------------
    # フェーズ5: GitHub push → Vercel デプロイ → site-annotator 登録 → スプレッドシート更新
    # ------------------------------------------------------------------

    def _phase5_deploy(
        self,
        case: CaseRecord,
        spec: dict[str, Any],
        site_dir: Path,
    ) -> str:
        """引数: site_dir（ビルド済み）/ spec（manus_deploy_github_url 参照）/ case（行番号）
        処理: GitHub push or Manus URL 利用 → Vercel デプロイ → site-annotator 登録 → シートに URL 書き込み
        出力: deploy_url
        """
        fallback_repo_name = sanitize_github_repo_name(
            case["partner_name"], str(case["record_number"]),
        )
        manus_git = (spec.get("manus_deploy_github_url") or "").strip()
        if manus_git:
            logger.info("› GitHub: Manus が push したリポジトリ URL を使用…")
            github_url = manus_git.rstrip("/")
            if not github_url.lower().endswith(".git"):
                github_url = f"{github_url}.git"
            try:
                _, vercel_project_name = github_owner_repo_from_clone_url(github_url)
            except ValueError:
                logger.warning(
                    "Manus の GitHub URL から owner/repo を解釈できません。sanitize 名を使います: %s",
                    manus_git,
                )
                vercel_project_name = fallback_repo_name
        else:
            logger.info("› GitHub にソースコードを push…")
            github_url = self.github_client.push_to_github(site_dir, fallback_repo_name, "test")
            vercel_project_name = fallback_repo_name

        vercel_name_for_api = sanitize_vercel_project_name(vercel_project_name)
        logger.info("› Vercel にデプロイ…（git=%s project=%s）", github_url, vercel_name_for_api)
        deployment = self.vercel_client.deploy_from_github(github_url, vercel_project_name)
        deploy_url = deployment["url"]

        logger.info("› デプロイ URL が開けるか確認…")
        if not self.vercel_client.verify_deployment_url(deploy_url):
            logger.warning("デプロイURLが閲覧できません: %s", deploy_url)

        # 引数: partner_name（=サイト名）/ deploy_url（Vercel 公開 URL）
        # 処理: POST /api/sites/provision — パートナー名・リポジトリURL・tracker.js の
        #   3チェック通過時のみサイト作成・crawl 実行（site-annotator 側で並列チェック）
        # 出力: 成功時は site id / share_token / crawl 件数をログ。失敗は warning のみ（続行）
        if SITE_PROVISION_API_URL and SITE_PROVISION_API_KEY:
            try:
                from modules.site_provision_client import provision_site

                logger.info("› site-annotator にサイトを登録…")
                provision_site(
                    api_url=SITE_PROVISION_API_URL,
                    api_key=SITE_PROVISION_API_KEY,
                    site_name=case["partner_name"],
                    site_url=deploy_url,
                )
            except Exception:
                logger.warning(
                    "site-annotator への登録に失敗しました（続行します）",
                    exc_info=True,
                )

        # 引数: deploy_url / github_url / row — 処理: AI列と AJ列を batchUpdate
        self.spreadsheet.update_deploy_url_and_complete_status(
            case["row_number"], deploy_url, github_repo_url=github_url,
        )
        logger.info("✓ 案件完了 — 公開 URL: %s", deploy_url)
        return deploy_url

    def run(self) -> None:
        """スプレッドシートから対象行を取り、各行を process_case で順に処理する。

        複数ターミナルで ``python main.py`` を同時起動する場合、各イテレーションで
        R 列を再読して他プロセスが既に "MacBot" を書き込んだ行はスキップする（重複着手の抑止）。
        """
        try:
            _uc = stream_supports_color(sys.stdout)
            logger.info(startup_title(use_color=_uc))

            # --- Manus 再開モード: R列の状態を無視してレコード番号で直接取得 ---
            if BOT_RESUME_FROM_MANUS:
                if not BOT_ONLY_RECORD_NUMBER:
                    logger.error(
                        "BOT_RESUME_FROM_MANUS=true には BOT_ONLY_RECORD_NUMBER が必須です"
                    )
                    return
                c = self.spreadsheet.get_case_by_record_number(BOT_ONLY_RECORD_NUMBER)
                if c is None:
                    logger.error(
                        "BOT_RESUME_FROM_MANUS: レコード番号 %r がシートに見つかりません",
                        BOT_ONLY_RECORD_NUMBER,
                    )
                    return
                cases = [c]
                logger.info(
                    "Manus 再開モード: record=%r row=%s を R 列の状態に関係なく取得",
                    BOT_ONLY_RECORD_NUMBER,
                    c.get("row_number"),
                )
            else:
                # SPREADSHEET_TARGET_AI_STATUS 等の条件でフィルタ済みのキュー
                cases = self.spreadsheet.get_pending_cases()

                if not cases:
                    logger.info(idle_banner(use_color=_uc))
                    return

                if BOT_ONLY_RECORD_NUMBER:
                    want = BOT_ONLY_RECORD_NUMBER
                    filtered = [
                        c
                        for c in cases
                        if str(c.get("record_number") or "").strip() == want
                    ]
                    if not filtered:
                        logger.warning(
                            "BOT_ONLY_RECORD_NUMBER=%r に一致する未処理案件がありません（キュー内 %s 件）",
                            want,
                            len(cases),
                        )
                        logger.info(idle_banner(use_color=_uc))
                        return
                    cases = filtered
                    logger.info(
                        "BOT_ONLY_RECORD_NUMBER により %s 件に絞り込み record=%r",
                        len(cases),
                        want,
                    )

            # テスト用: 先頭 N 件だけ処理（未設定なら全件）
            if BOT_MAX_CASES:
                cases = cases[:BOT_MAX_CASES]

            logger.info(
                batch_start_banner(
                    count=len(cases),
                    max_cases=BOT_MAX_CASES or None,
                    use_color=_uc,
                )
            )

            # 1 件失敗してもループは続ける（各 process_case が例外を投げうる）
            for case in cases:
                try:
                    row_n = int(case["row_number"])
                    r_now = self.spreadsheet.get_ai_status_cell(row_n)
                    if not BOT_RESUME_FROM_MANUS and ai_cell_excludes_from_pending_queue(r_now):
                        logger.info(
                            "スキップ（他プロセスが着手済み、R 列が非空） "
                            "row=%s record=%s R=%r",
                            case.get("row_number"),
                            case.get("record_number"),
                            r_now[:120] if r_now else "",
                        )
                        continue
                    self.process_case(case)
                except Exception as e:
                    # process_case 内で既に exc_info 付きログ済みのため、ここは要約のみ
                    logger.error(
                        "案件が失敗しましたがバッチは続行します row=%s record=%s: %s",
                        case.get("row_number"),
                        case.get("record_number"),
                        e,
                    )

            logger.info(all_done_banner(use_color=_uc))

        except Exception as e:
            logger.error("Bot実行エラー: %s", e, exc_info=True)
            raise


def _emit_startup_validation(result: StartupValidationResult, *, to_stdout: bool) -> bool:
    """検証結果をログまたは標準出力へ出す。戻り値は result.ok（呼び出し側が exit 判定に使う）。"""
    if to_stdout:
        for w in result.warnings:
            print(f"WARN: {w}")
        for err in result.errors:
            print(f"ERROR: {err}")
        return result.ok
    for w in result.warnings:
        logger.warning("[設定] %s", w)
    if not result.ok:
        for err in result.errors:
            logger.error("[設定] %s", err)
    return result.ok


def _run_startup_validation() -> bool:
    """.env 等の必須設定を検証。失敗時は False（呼び出し側が exit）。"""
    return _emit_startup_validation(
        validate_startup_config(require_full_pipeline=True),
        to_stdout=False,
    )


def _spreadsheet_header_issues(spreadsheet: SpreadsheetClient) -> list[str]:
    """列見出し検証の結果メッセージ一覧（本番・スナップショットで共通）。"""
    return spreadsheet.validate_header_labels()


def _react_to_spreadsheet_header_issues(issues: list[str], *, to_stdout: bool) -> None:
    """列見出し不一致をログまたは標準出力へ出し、厳格モードなら sys.exit(1)。"""
    if to_stdout:
        for m in issues:
            print(f"HEADER_MISMATCH: {m}")
        if SPREADSHEET_HEADERS_STRICT and issues:
            print(
                "ERROR: 列見出し不一致のため終了（SPREADSHEET_HEADERS_STRICT=true。"
                " R・AI・AJ は検証対象外）"
            )
            sys.exit(1)
        return
    for msg in issues:
        if SPREADSHEET_HEADERS_STRICT:
            logger.error("[起動時・列見出し] %s", msg)
        else:
            logger.warning("[起動時・列見出し] %s", msg)
    if SPREADSHEET_HEADERS_STRICT and issues:
        logger.error(
            "列見出し不一致のため起動を中止します。"
            "config.py の SPREADSHEET_HEADER_LABELS をシート1行目に合わせるか（R・AI・AJ は検証対象外）、"
            "SPREADSHEET_HEADERS_STRICT=false で警告のみにしてください。"
        )
        sys.exit(1)


def _apply_spreadsheet_header_validation(
    spreadsheet: SpreadsheetClient, *, to_stdout: bool
) -> None:
    """列見出しを検証。厳格モードで不一致があれば sys.exit(1)。"""
    _react_to_spreadsheet_header_issues(
        _spreadsheet_header_issues(spreadsheet),
        to_stdout=to_stdout,
    )


def main() -> None:
    """
    エントリポイント。

    通常: 起動検証 → WebsiteBot 生成 → 列見出し確認 → run()。
    BOT_CONFIG_CHECK=1: 上記と同じ検証を標準出力に出して終了（案件は処理しない）。
    """
    # ---- 診断モード: 本番と同じ検証ロジックを print し、問題なければ 0 で終了 ----
    if os.getenv("BOT_CONFIG_CHECK", "").strip().lower() in ("1", "true", "yes"):
        logging.getLogger().setLevel(logging.INFO)
        cfg_result = validate_startup_config(require_full_pipeline=True)
        if not _emit_startup_validation(cfg_result, to_stdout=True):
            sys.exit(1)
        try:
            _react_to_spreadsheet_header_issues(
                _spreadsheet_header_issues(SpreadsheetClient()),
                to_stdout=True,
            )
        except Exception as e:
            print(f"ERROR: スプレッドシート列検証で例外: {e}")
            sys.exit(1)
        print("OK: 設定・列見出し検証に問題ありません。")
        sys.exit(0)

    # ---- 本番起動: Sheets / GitHub / Vercel / API キー等 ----
    if not _run_startup_validation():
        sys.exit(1)

    try:
        bot = WebsiteBot()
        _apply_spreadsheet_header_validation(bot.spreadsheet, to_stdout=False)
        bot.run()
    except KeyboardInterrupt:
        # Ctrl+C
        logger.info("Botを停止しました")
    except Exception as e:
        # run() 外の想定外（初期化失敗など）
        logger.error("予期しないエラー: %s", e, exc_info=True)
        sys.exit(1)


# python main.py 実行時の起点（pytest 等から import しただけでは呼ばれない）
if __name__ == "__main__":
    main()
