"""案件15826 をヒアリングシート本文直接指定で最後まで実行するスクリプト。

スプレッドシートにヒアリングシート情報がないため、
hearing_sheet_content を直接渡して Phase1〜5 を通す。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.logging_setup import configure_logging

configure_logging()

import logging
from typing import Any

from config.config import get_contract_plan_info
from modules.case_extraction import ExtractedHearingBundle
from modules.contract_workflow import (
    ContractWorkBranch,
    resolve_contract_work_branch,
    resolve_work_branch_with_basic_lp_override,
)
from modules.llm.llm_raw_output import write_llm_raw_artifacts_phase2_snapshot
from modules.llm.llm_step_trace import begin_case_llm_trace, end_case_llm_trace
from modules.llm.text_llm_stage import run_text_llm_stage
from main import WebsiteBot

logger = logging.getLogger("run_15826")

RECORD_NUMBER = "15826"

HEARING_SHEET_CONTENT = """\
============================================================
  ホームページ制作 ヒアリングシート
  クライアント：株式会社ReVALUE
============================================================

【0】ご契約名義（営業担当より共有いたします。未共有の場合はご連絡ください）
→ 株式会社ReVALUE

【1】あなたのお名前・会社名を教えてください
→ 屋宜 宣一郎／株式会社ReVALUE

【2】今回のホームページ制作では、「新規サイト制作」と「現状サイトのリニューアル」のどちらをご希望でしょうか？
→ 新規サイト制作

【2.1】リニューアルの目的はなんですか？（※質問2でリニューアルと答えた方のみ）
→ （該当なし：新規サイト制作のため）

【3】ホームページの目的をお教えください
→ 信頼性の獲得

【4】コーポレートサイトとランディングページどちらを希望しますか？
→ コーポレートサイト（例：https://www.watarukensetsu.net/）

【5】ブログ機能はご利用になりますか？
→ はい

【6】SNSの連携をしますか？
→ はい

【7】ホームページに使いたい色を教えてください
→ 白、紺、黒、一部カラフル（SNSを連想させる色合い）

【8】ホームページで希望の雰囲気を教えてください
→ カッコいい

【9】ホームページのデザインで参考にしたいサイトのURLを教えてください
→ ・https://applied-g.jp/digital_promotion/sns-oa/
　　体制と運用フロー・料金プランが掲載されているところ。

　・https://nomark-inc.co.jp/case/category/sns-consulting
　　契約事例が載っているSNS運用のところ

　・https://shining-okinawa.jp/business/sns-support/
　　多言語対応の部分

【10】電話番号と電話受付時間を教えてください（載せない場合は「無」とご回答ください）
→ 無し　平日9時〜17時（土日祝祭日休み）

【11】メールアドレスを教えてください（載せない場合は「無」とご回答ください）
→ info@re-valuegroup.com

【12】住所を教えてください（載せない場合は「無」とご回答ください）
→ 〒901-1207 沖縄県南城市大里字古堅967-1

【13】SNSがある場合、URLを教えてください
→ 作成中

【14】ロゴはお持ちでしょうか？（※お持ちの場合、公式LINEまたはメールにて添付をお願いします。）
→ （未回答）

【15】既にホームページをお持ちの場合、URLをお教えください
→ 無し

【16】お問い合わせ先はどこに設定しますか？（複数回答可）
→ お問い合わせフォーム（通知先のメールアドレス）、電話（お問い合わせ用電話番号）、LINE（LINEアカウント）、SNS（Instagram、Xなど）

【17】主な事業分野は何ですか？
→ SNS運用代行・SNSコンサル・Instagram収益化コンサル

【18】提供する商品やサービスの詳細を教えてください。
→ 別紙のとおり事業計画書を送ります。

【19】商品やサービスの主な特徴と独自性を教えてください
→ 別紙のとおり事業計画書を送ります。

【20】あなたが事業を行う上で大切にしていることを教えてください（企業ミッションやコンセプトも可）
→ 別紙のとおり

【21】競合他社はどこですか？
→ （未回答）

【22】競合他社と比較して、貴社の強みは何ですか？
→ 高単価のイメージのあるSNS運用代行も個人事業主や小規模事業者でも取り入れやすい低単価のプランもあります。本格的に運用して会社の人材採用や集客、イメージプロモーションに活用したい方向けのプランも用意

【23】これまでにどんな成果を上げてきましたか？（まだ開業していない場合などは「無」とお答えください）
→ リール動画制作（スポーツスクールの集客、海外ツアーの集客動画、自治体のブランディング）

【24】お客さんからの反応や満足度はどのようなものですか？（まだ開業していない場合などは「無」とお答えください）
→ 無し（ダンススクールは生徒が満員で売り上げUPなど）

【25】あなたのサービスを提供できる地域が限られている場合は、提供できる地域の範囲を教えてください
→ 沖縄県全域

【26】採用情報を掲載する場合、どのような内容を載せたいか回答お願いします
→ 職種・ポジション、仕事内容、求める人物像、勤務地、勤務時間、雇用形態、給与

【27】あなたの事業のターゲットの性別を教えてください
→ 両方

【28】あなたの事業のターゲットの世代を教えてください（複数回答可）
→ 20代、30代、40代、50代

【29】あなたの事業のターゲット層を教えてください
→ 両方

【30】上記以外で伝えたいことがあれば教えてください
→ 事業内容は別でPDFでお送りします。
"""


def run() -> None:
    bot = WebsiteBot()

    # --- スプレッドシートから案件メタ情報を取得 ---
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

    # --- ヒアリングバンドルを直接構築（スプレッドシートのヒアリング列をバイパス）---
    bundle = ExtractedHearingBundle(
        hearing_sheet_content=HEARING_SHEET_CONTENT,
        appo_memo=str(case.get("appo_memo") or ""),
        sales_notes=str(case.get("sales_notes") or ""),
    )

    # --- 作業分岐の解決 ---
    plan_raw = (case.get("contract_plan") or "").strip()
    plan_info = get_contract_plan_info(plan_raw)
    work_branch = resolve_work_branch_with_basic_lp_override(
        case["contract_plan"],
        record_number=RECORD_NUMBER,
        partner_name=str(case.get("partner_name") or ""),
        lookup_basic_is_landing_page=bot.spreadsheet.lookup_basic_is_landing_page,
    )
    logger.info(
        "契約プラン: plan=%r branch=%s pages=%s type=%s",
        plan_raw,
        work_branch.value,
        plan_info.get("pages"),
        plan_info.get("type"),
    )

    # --- R列にステータス書き込み ---
    bot.spreadsheet.update_ai_status(case["row_number"], "MacBot")

    # --- LLM トレース開始 ---
    begin_case_llm_trace(RECORD_NUMBER)

    try:
        # --- Phase 2: TEXT_LLM ---
        logger.info("【Phase 2】TEXT_LLM 開始… branch=%s", work_branch.value)
        req, spec = run_text_llm_stage(
            bundle,
            contract_plan=case["contract_plan"],
            partner_name=case["partner_name"],
            record_number=RECORD_NUMBER,
            work_branch=work_branch,
        )

        site_name = f"{case['partner_name']}-{case['record_number']}"
        write_llm_raw_artifacts_phase2_snapshot(
            site_name=site_name,
            spec=spec,
            requirements_result=req,
            work_branch=work_branch,
        )

        # --- Phase 3: サイト準備 ---
        logger.info("【Phase 3】サイト出力先準備…")
        site_dir = bot._phase3_prepare_site(case, req, spec, work_branch)

        # --- Phase 4: ビルド ---
        logger.info("【Phase 4】ビルド検証…")
        bot._phase4_build(case, spec, site_dir, work_branch, plan_info)

        # --- Phase 5: デプロイ ---
        logger.info("【Phase 5】デプロイ…")
        deploy_url = bot._phase5_deploy(case, spec, site_dir)

        logger.info("完了！デプロイ URL: %s", deploy_url)

    finally:
        end_case_llm_trace()


if __name__ == "__main__":
    run()
