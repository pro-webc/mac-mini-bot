"""仕様書生成のラッパー・ヒアリング取得。実体は `modules.llm_mock` のモック TEXT_LLM。

正常ルート以外でのフォールバックは行わない（README「エラー処理の原則」参照）。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

import requests
from config.config import get_contract_plan_info
from modules.llm_mock import build_spec_dict_mock

logger = logging.getLogger(__name__)

def _briefing_value_as_text(v: Any) -> str:
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(v)
    return str(v)


def _plan_info_as_briefing_lines(plan_info: Dict[str, Any]) -> str:
    lines: list[str] = []
    for k in sorted(plan_info.keys()):
        v = plan_info.get(k)
        if v is None or v == "":
            continue
        lines.append(f"- {k}: {_briefing_value_as_text(v)}")
    return "\n".join(lines) if lines else "（項目なし）"


def compose_spec_input_briefing(
    *,
    partner_name: str,
    contract_plan: str,
    contract_pages: int,
    page_rule: str,
    plan_info: Dict[str, Any],
    hearing_sheet_content: str,
    site_build_prompt: str,
    requirements_result: Dict[str, Any],
    max_chars: int = 120_000,
) -> str:
    """
    仕様生成向けの入力を **JSONではなくプレーンテキスト1本**にまとめる（テスト・手動検証用）。
    （出力形式は Markdown サイト台本＋末尾 YAML。レガシー運用では JSON のみも解釈可）
    """
    chunks: list[str] = []
    chunks.append("【パートナー名】")
    chunks.append((partner_name or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約プラン（システム）】")
    chunks.append((contract_plan or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約ページ数（厳守・変更禁止）】")
    chunks.append(str(contract_pages))
    chunks.append("")
    chunks.append("【ページ構成に関する指示】")
    chunks.append(page_rule.strip())
    chunks.append("")
    chunks.append("【契約プラン詳細（システム・テキスト化）】")
    chunks.append(_plan_info_as_briefing_lines(plan_info))
    chunks.append("")
    chunks.append("【ヒアリング原文】")
    chunks.append((hearing_sheet_content or "").strip() or "（空）")
    chunks.append("")
    chunks.append("【サイト制作マスタープロンプト（最優先）】")
    chunks.append(site_build_prompt.strip())
    chunks.append("")

    pt = requirements_result.get("plan_type")
    if pt:
        chunks.append("【システム確定 plan_type】")
        chunks.append(str(pt))
        chunks.append("")

    cm = requirements_result.get("contract_max_pages")
    if cm is not None:
        chunks.append("【contract_max_pages（参照）】")
        chunks.append(str(cm))
        chunks.append("")

    cv = requirements_result.get("client_voice")
    if isinstance(cv, str) and cv.strip():
        sbp_head = site_build_prompt.strip()[:400]
        if cv.strip()[:400] != sbp_head:
            chunks.append("【client_voice（補足・テキスト）】")
            chunks.append(cv.strip())
            chunks.append("")

    ibn = requirements_result.get("internal_build_notes")
    if isinstance(ibn, list) and ibn:
        chunks.append("【内部メモ（サイト非掲載・参照のみ）】")
        for x in ibn:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    oq = requirements_result.get("open_questions")
    if isinstance(oq, list) and oq:
        chunks.append("【要確認事項】")
        for x in oq:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    facts = requirements_result.get("facts")
    if isinstance(facts, dict) and facts:
        chunks.append("【補足ファクト（テキスト化）】")
        for fk, fv in facts.items():
            if fv is None or fv == "":
                continue
            if isinstance(fv, list):
                chunks.append(f"- {fk}:")
                for it in fv:
                    chunks.append(f"  - {it}")
            else:
                chunks.append(f"- {fk}: {_briefing_value_as_text(fv)}")
        chunks.append("")

    out = "\n".join(chunks).strip()
    if len(out) > max_chars:
        logger.warning(
            "仕様入力ブリーフが長いため %s 文字に切り詰めました（元 %s）",
            max_chars,
            len(out),
        )
        half = max_chars // 2 - 80
        out = (
            out[:half]
            + "\n\n…[truncated]…\n\n"
            + out[-half:]
        )
    return out


class SpecGenerator:
    """ヒアリング取得と、モック TEXT_LLM による仕様 dict 生成の薄いラッパー。"""

    def __init__(self) -> None:
        pass

    def fetch_hearing_sheet(self, url: str) -> Optional[str]:
        """
        ヒアリングシートの内容を取得

        Args:
            url: ヒアリングシートURL

        Returns:
            ヒアリングシートの内容（テキスト）
        """
        try:
            raw = (url or "").strip()
            if not raw:
                return None
            # セルに全文が貼られているだけの場合（http で始まらない）
            if not re.match(r"^https?://", raw, re.IGNORECASE):
                m = re.search(r"https?://[^\s\]<>\")]+", raw)
                if m:
                    return self.fetch_hearing_sheet(m.group(0))
                logger.info(
                    "ヒアリングシート列が URL ではないため、本文としてそのまま使用します（先頭 %s 文字）",
                    min(len(raw), 200),
                )
                return raw

            # Google Sheets URLの場合
            if "docs.google.com/spreadsheets" in raw:
                # 簡易的な取得（実際はGoogle Sheets APIを使用）
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    # HTMLからテキストを抽出（簡易版）
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text()
                    logger.info("ヒアリングシートを取得しました")
                    return text
            else:
                # その他のURL
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    return response.text

            return None
        except Exception as e:
            logger.error(f"ヒアリングシート取得エラー: {e}")
            return None

    def generate_spec(
        self,
        hearing_sheet_content: str,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str,
    ) -> Dict:
        """
        `modules.llm_mock.build_spec_dict_mock` へ委譲（後方互換・単体テスト用）。
        """
        plan_info = get_contract_plan_info(contract_plan)
        contract_pages = int(plan_info.get("pages") or 1)
        page_rule = (
            "サイト台本は **トップ（/）のみ**の単一ページ構成とすること（`## ページ:` は `/` のみ）。"
            if contract_pages <= 1
            else (
                f"サイト台本に **`## ページ: /...` でちょうど {contract_pages} 個のルート**（それぞれ一意のパス）を書くこと。"
                "コンテンツが薄くてもページを統合・省略して数を減らさない。"
                "トップを含め、一覧・詳細・問い合わせ等へ内容を配分してよい。"
            )
        )
        sbp = (requirements_result.get("site_build_prompt") or "").strip()
        if not sbp:
            cv = requirements_result.get("client_voice")
            if isinstance(cv, str) and cv.strip():
                sbp = (
                    "【互換: site_build_prompt が無いため client_voice を主入力とする】\n"
                    + cv.strip()
                )
            else:
                sbp = (
                    "【互換: 要約のみ】\n"
                    + json.dumps(requirements_result, ensure_ascii=False, indent=2)[:8000]
                )
        _ = compose_spec_input_briefing(
            partner_name=partner_name,
            contract_plan=contract_plan,
            contract_pages=contract_pages,
            page_rule=page_rule,
            plan_info=plan_info,
            hearing_sheet_content=hearing_sheet_content or "",
            site_build_prompt=sbp,
            requirements_result=requirements_result,
        )
        return build_spec_dict_mock(
            hearing_sheet_content,
            requirements_result,
            contract_plan,
            partner_name,
        )
