"""メインオーケストレーション

完成サイトを GitHub に push し Vercel で公開するまでを一本化する。

パイプライン概略:
  1. ヒアリングシート類の抽出（`modules.case_extraction`）
  2. TEXT_LLM（`modules.llm.text_llm_stage` — プランは ``BRANCH_REGISTRY`` で分岐。各 ``*_USE_CLAUDE_MANUAL`` と Claude CLI の認証が必要）
  3. 出力先ディレクトリ準備（テンプレコピーなし）→ `llm_raw_output/` に LLM 生出力を保存
     （Manus 待ちで 3 に進めない間は `output/phase2_llm_checkpoints/…/pre_manus/` に TEXT_LLM（Claude CLI）分のみ先行保存）
  4. GitHub push → Vercel デプロイ → site-annotator 登録 → スプレッドシートに公開 URL

各段の LLM 割当は ``docs/pipeline/LLM_PIPELINE.md`` を参照。
"""
from __future__ import annotations

import atexit
import contextlib
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

from config.logging_setup import configure_logging

# 他 import より先にログ設定（import 時のログレベルが揃う）
configure_logging()

from config.config import (
    BOT_MAX_CASES,
    BOT_ONLY_RECORD_NUMBER,
    GA4_INJECT_TRACKING,
    GA4_MEASUREMENT_ID,
    OUTPUT_DIR,
    SITE_PROVISION_API_KEY,
    SITE_PROVISION_API_URL,
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN,
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
from modules.ga4_injector import inject_ga4_tracking
from modules.github_client import GitHubClient, sanitize_github_repo_name
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_llm_raw_artifacts_phase2_snapshot,
    write_manus_only_style_run_artifacts,
)
from modules.llm.llm_step_trace import begin_case_llm_trace, end_case_llm_trace
from modules.llm.text_llm_stage import run_text_llm_stage
from modules.site_generator import SiteGenerator
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
        self.spec_generator = SpecGenerator(sheets_service=self.spreadsheet.service)
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
    # 行番号の再解決
    # ------------------------------------------------------------------

    def _refresh_case_row(self, case: CaseRecord) -> None:
        """レコード番号+パートナー名でシート上の現在の行番号を再取得し case を更新する。

        行の挿入・削除で行番号がずれうるため、スプレッドシートへの書き込み前に呼ぶ。
        解決に失敗した場合は元の row_number を維持して warning を出す。
        """
        try:
            new_row = self.spreadsheet.resolve_current_row(
                str(case.get("record_number") or ""),
                str(case.get("partner_name") or ""),
            )
        except Exception:
            logger.warning(
                "行番号の再解決に失敗しました（元の row=%s を維持） record=%s",
                case.get("row_number"), case.get("record_number"),
                exc_info=True,
            )
            return
        old_row = case.get("row_number")
        if new_row != old_row:
            logger.info(
                "行番号が変わりました record=%s partner=%s: row %s → %s",
                case.get("record_number"), case.get("partner_name"),
                old_row, new_row,
            )
            case["row_number"] = new_row

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

        self._refresh_case_row(case)
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
                self._refresh_case_row(case)
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
            self._refresh_case_row(case)
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
        処理: BRANCH_REGISTRY でパイプライン選択
        出力: (requirements_result, spec)
        """
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

        # manus_deploy_github_url があれば Manus が完成リポを push 済みなので
        # フェンス解析より shallow clone を優先する（部分抽出による不整合を防止）
        if manus_git_for_fallback:
            logger.info(
                "manus_deploy_github_url があるため GitHub を shallow clone してサイト全体を取得します: %s",
                manus_git_for_fallback,
            )
            self.github_client.shallow_clone_repo_into_site_dir(manus_git_for_fallback, site_dir)
        else:
            n_gen = apply_contract_outputs_to_site_dir(spec, site_dir, work_branch=work_branch)
            if n_gen:
                logger.info("› フェンス解析でサイトに %s ファイル反映（分岐 %s）", n_gen, work_branch.value)
            elif work_branch in BRANCH_REGISTRY and claude_manual_enabled_for_branch(work_branch):
                raise RuntimeError(
                    "生成マークダウンからサイトファイルを1件も適用できませんでした。"
                    " manus_deploy_github_url も無いため続行できません。"
                    " Manus の返答を確認してください。"
                )

        # 引数: site_dir（フェンス適用 or shallow clone 完了済み）/ GA4_MEASUREMENT_ID（環境変数、任意）
        # 処理: app/layout.tsx に <Script> で CTA トラッキングを注入し、
        #   public/scripts/ga4-cta-tracking.js を配置する（modules.ga4_injector）。
        #   GA4_INJECT_TRACKING=true なら ID なしでもタグだけ注入（後から ID 追加可能）
        # 出力: 注入成功ログ。GA4_INJECT_TRACKING=false かつ ID 未設定ならスキップ
        #
        # Manus フロー: Vercel は Manus の GitHub から直接ビルドするため、
        # ローカルへの GA4 注入はデプロイに反映されない → スキップ
        if GA4_INJECT_TRACKING:
            if manus_git_for_fallback:
                logger.info(
                    "GA4 注入スキップ: Manus の GitHub からデプロイするため"
                    " ローカルへの注入は本番に反映されない"
                )
            else:
                inject_ga4_tracking(site_dir, measurement_id=GA4_MEASUREMENT_ID)

        return site_dir

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
        # 出力: 成功時は修正ツール共有 URL（AK列に書き込む）。失敗は warning のみ（続行）
        correction_tool_url = ""
        if SITE_PROVISION_API_URL and SITE_PROVISION_API_KEY:
            try:
                from modules.site_provision_client import build_share_url, provision_site

                logger.info("› site-annotator にサイトを登録…")
                provision_data = provision_site(
                    api_url=SITE_PROVISION_API_URL,
                    api_key=SITE_PROVISION_API_KEY,
                    site_name=case["partner_name"],
                    site_url=deploy_url,
                )
                correction_tool_url = build_share_url(provision_data) or ""
                if correction_tool_url:
                    logger.info("› 修正ツール URL: %s", correction_tool_url)
            except Exception:
                logger.warning(
                    "site-annotator への登録に失敗しました（続行します）",
                    exc_info=True,
                )

        # 引数: deploy_url / github_url / correction_tool_url / row
        # 処理: AI列・AJ列・AK列（修正ツールURL、取得できた場合のみ）を batchUpdate
        # 長時間処理の後で行番号がずれている場合があるため再解決する
        self._refresh_case_row(case)
        self.spreadsheet.update_deploy_url_and_complete_status(
            case["row_number"], deploy_url,
            github_repo_url=github_url,
            correction_tool_url=correction_tool_url,
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
                    self._refresh_case_row(case)
                    row_n = int(case["row_number"])
                    r_now = self.spreadsheet.get_ai_status_cell(row_n)
                    if ai_cell_excludes_from_pending_queue(r_now):
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


_CAFFEINATE_PID_FILE = Path(__file__).resolve().parent / ".caffeinate.pid"


def _kill_orphaned_caffeinate() -> None:
    """前回実行で孤立した caffeinate がいれば終了させる。"""
    if not _CAFFEINATE_PID_FILE.exists():
        return
    try:
        pid = int(_CAFFEINATE_PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGKILL)
        logger.info("前回の孤立 caffeinate (pid=%s) を終了しました", pid)
    except (ValueError, ProcessLookupError, PermissionError):
        pass
    finally:
        _CAFFEINATE_PID_FILE.unlink(missing_ok=True)


def _stop_caffeinate(proc: subprocess.Popen[Any]) -> None:
    """caffeinate プロセスを停止し PID ファイルを削除する。"""
    if proc.poll() is not None:
        _CAFFEINATE_PID_FILE.unlink(missing_ok=True)
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    _CAFFEINATE_PID_FILE.unlink(missing_ok=True)
    logger.info("スリープ抑止を解除しました")


@contextlib.contextmanager
def _prevent_sleep() -> Iterator[None]:
    """macOS の caffeinate でアイドル／システムスリープを抑止する。

    PID ファイルで caffeinate のライフサイクルを管理する。
    - 起動時: 前回の孤立プロセスがあればクリーンアップ
    - 終了時: finally + atexit + SIGTERM ハンドラの三重保護で確実に停止
    caffeinate が使えない環境では warning だけ出して続行する。
    """
    _kill_orphaned_caffeinate()

    try:
        proc = subprocess.Popen(
            ["caffeinate", "-i", "-s"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        logger.warning("caffeinate が見つかりません — スリープ抑止をスキップします")
        yield
        return

    _CAFFEINATE_PID_FILE.write_text(str(proc.pid))
    logger.info("スリープ抑止を開始しました (caffeinate pid=%s)", proc.pid)

    # atexit: finally が実行されないケース (os._exit 等) の保険
    atexit.register(_stop_caffeinate, proc)

    # SIGTERM: systemd stop / kill <pid> への対応
    prev_handler = signal.getsignal(signal.SIGTERM)

    def _sigterm_handler(signum: int, frame: Any) -> None:
        _stop_caffeinate(proc)
        if callable(prev_handler) and prev_handler not in (
            signal.SIG_DFL,
            signal.SIG_IGN,
        ):
            prev_handler(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, _sigterm_handler)

    try:
        yield
    finally:
        _stop_caffeinate(proc)
        atexit.unregister(_stop_caffeinate)
        signal.signal(signal.SIGTERM, prev_handler)


def _run_startup_validation() -> bool:
    """.env 等の必須設定を検証。失敗時は False（呼び出し側が exit）。"""
    return _emit_startup_validation(
        validate_startup_config(require_full_pipeline=True),
        to_stdout=False,
    )


def main() -> None:
    """
    エントリポイント。

    通常: 起動検証 → WebsiteBot 生成（列自動検出含む）→ run()。
    BOT_CONFIG_CHECK=1: 上記と同じ検証を標準出力に出して終了（案件は処理しない）。
    """
    # ---- 診断モード: 本番と同じ検証ロジックを print し、問題なければ 0 で終了 ----
    if os.getenv("BOT_CONFIG_CHECK", "").strip().lower() in ("1", "true", "yes"):
        logging.getLogger().setLevel(logging.INFO)
        cfg_result = validate_startup_config(require_full_pipeline=True)
        if not _emit_startup_validation(cfg_result, to_stdout=True):
            sys.exit(1)
        try:
            client = SpreadsheetClient()
            print(f"OK: 列位置を自動検出しました: {client.columns}")
        except Exception as e:
            print(f"ERROR: スプレッドシート列検出で例外: {e}")
            sys.exit(1)
        print("OK: 設定・列見出し検証に問題ありません。")
        sys.exit(0)

    # ---- 本番起動: Sheets / GitHub / Vercel / API キー等 ----
    if not _run_startup_validation():
        sys.exit(1)

    with _prevent_sleep():
        try:
            bot = WebsiteBot()
            bot.run()
        except KeyboardInterrupt:
            logger.info("Botを停止しました")
        except Exception as e:
            logger.error("予期しないエラー: %s", e, exc_info=True)
            sys.exit(1)


# python main.py 実行時の起点（pytest 等から import しただけでは呼ばれない）
if __name__ == "__main__":
    main()
