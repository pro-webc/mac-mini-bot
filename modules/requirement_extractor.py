"""第1段: ヒアリング類 → サイト制作マスタープロンプト（プレーンテキスト）

LLM 応答は原則 **本文のみ**（JSON 禁止）。`plan_type` / `contract_max_pages` は契約からコード側で付与。
旧JSON応答は `{` 始まりのときのみ互換パースする。
正常ルート以外でのフォールバックは行わない（README「エラー処理の原則」参照）。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from config.config import get_contract_plan_info
from config.prompt_settings import format_prompt, get_prompt_str
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)

# 第1段の site_build_prompt として許容する最小文字数（プロンプト上はより長い分量を求める）
_MIN_SITE_BUILD_PROMPT_CHARS = 400


def _json_from_llm(text: str) -> Optional[Dict[str, Any]]:
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return None


def expected_plan_type(plan_info: Dict) -> str:
    """契約プランから、抽出結果に期待する plan_type。"""
    if plan_info.get("type") == "landing_page":
        return "basic_lp"
    if plan_info.get("name") == "BASIC" and plan_info.get("pages") == 1:
        return "basic"
    if plan_info.get("type") == "website" and int(plan_info.get("pages") or 0) > 1:
        name = (plan_info.get("name") or "").upper()
        return "advance" if name == "ADVANCE" else "standard"
    return "general"


def _build_unified_extraction_prompt(
    plan_info: Dict,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
) -> str:
    max_pages = int(plan_info.get("pages") or 1)
    return format_prompt(
        "requirement_extraction.user_template",
        plan_info_json=json.dumps(plan_info, ensure_ascii=False, indent=2),
        max_pages=str(max_pages),
        hearing_sheet_content=hearing_sheet_content,
        appo_memo=appo_memo,
        sales_notes=sales_notes,
    )


def _unwrap_plaintext_llm_output(text: str) -> str:
    """LLM が全体を ``` で囲んだ場合に中身だけ取り出す。"""
    s = (text or "").strip()
    if not s.startswith("```"):
        return s
    first_nl = s.find("\n")
    if first_nl == -1:
        return s
    body = s[first_nl + 1 :]
    fence = body.rfind("```")
    if fence != -1:
        body = body[:fence]
    return body.strip()


def _finalize_plain_prompt(
    site_build_prompt: str,
    *,
    expected_plan_type: str,
    max_pages: int,
) -> Dict[str, Any]:
    stripped = site_build_prompt.strip()
    if len(stripped) < _MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            f"要望抽出: 第1段のテキストが短すぎます（{len(stripped)} 文字）。"
            f"最低 {_MIN_SITE_BUILD_PROMPT_CHARS} 文字以上の制作プロンプトにしてください。"
            " modules.requirement_extractor"
        )
    return {
        "plan_type": expected_plan_type,
        "site_build_prompt": stripped,
        "internal_build_notes": [],
        "facts": {},
        "open_questions": [],
        "client_voice": stripped[:2000],
        "contract_max_pages": max_pages,
    }


def validate_requirements_result(
    data: Any,
    *,
    expected: str,
    max_pages: int,
) -> Dict[str, Any]:
    """
    LLM が返した requirements_result を検証し、contract_max_pages を付与する。
    """
    if not isinstance(data, dict):
        raise RuntimeError(
            "要望抽出: requirements_result がオブジェクトではありません。"
            " modules.requirement_extractor.validate_requirements_result"
        )

    pt = data.get("plan_type")
    if not pt:
        raise RuntimeError(
            "要望抽出: requirements_result に plan_type がありません。"
            " modules.requirement_extractor"
        )
    if str(pt) != expected:
        raise RuntimeError(
            f"要望抽出: plan_type が契約と不一致です（期待: {expected!r}, 実際: {pt!r}）。"
            " modules.requirement_extractor"
        )

    sbp = data.get("site_build_prompt")
    if not (isinstance(sbp, str) and sbp.strip()):
        raise RuntimeError(
            "要望抽出: site_build_prompt が空または文字列ではありません。"
            "（第1段はサイト制作用マスタープロンプトを出力する必要があります）"
            " modules.requirement_extractor"
        )
    stripped_prompt = sbp.strip()
    if len(stripped_prompt) < _MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            f"要望抽出: site_build_prompt が短すぎます（{len(stripped_prompt)} 文字）。"
            f"最低 {_MIN_SITE_BUILD_PROMPT_CHARS} 文字以上の指示書にしてください。"
            " modules.requirement_extractor"
        )

    facts = data.get("facts")
    if facts is None:
        facts = {}
    elif not isinstance(facts, dict):
        raise RuntimeError(
            "要望抽出: facts はオブジェクトまたは省略である必要があります。"
            " modules.requirement_extractor"
        )
    oq = data.get("open_questions")
    if oq is not None and not isinstance(oq, list):
        raise RuntimeError(
            "要望抽出: open_questions は配列または省略である必要があります。"
            " modules.requirement_extractor"
        )

    out = dict(data)
    out["facts"] = facts
    out["site_build_prompt"] = stripped_prompt
    out.pop("page_budget", None)
    out.pop("contract_max_pages", None)
    out["contract_max_pages"] = max_pages
    # 後方互換: スプレッドシート等が client_voice を参照する場合向け
    if not (isinstance(out.get("client_voice"), str) and str(out.get("client_voice")).strip()):
        bs = out.get("brief_summary")
        if isinstance(bs, str) and bs.strip():
            out["client_voice"] = bs.strip()
        else:
            out["client_voice"] = stripped_prompt[:2000]
    # 第2段へ渡すがサイト文案に出さないメモ（プロンプト必須・LLM が省略や型ミスしうる）
    _ibn = out.get("internal_build_notes")
    if _ibn is None:
        out["internal_build_notes"] = []
    elif isinstance(_ibn, list):
        out["internal_build_notes"] = [str(x) for x in _ibn if x is not None]
    else:
        logger.warning(
            "要望抽出: internal_build_notes が配列ではないため [] に正規化しました。"
        )
        out["internal_build_notes"] = []
    return out


class RequirementExtractor:
    """ヒアリング類からサイト制作マスタープロンプトを設計（LLM 1 回）"""

    def __init__(self) -> None:
        if not is_text_llm_configured():
            raise ValueError(
                "テキスト LLM が未設定です。"
                "TEXT_LLM_PROVIDER=cursor_agent_cli または claude_code_cli と、"
                "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
                "（要望・仕様・サイト実装はすべてターミナル CLI 経由です）"
            )

    def _llm(self, prompt: str, system: str, temperature: float = 0.3) -> str:
        return text_llm_complete(user=prompt, system=system, temperature=temperature)

    def extract_requirements(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str,
        contract_plan: str,
    ) -> Dict:
        plan_info = get_contract_plan_info(contract_plan)
        expected = expected_plan_type(plan_info)
        max_pages = int(plan_info.get("pages") or 1)

        user = _build_unified_extraction_prompt(
            plan_info,
            hearing_sheet_content,
            appo_memo,
            sales_notes,
        )
        try:
            raw = self._llm(
                user,
                get_prompt_str("requirement_extraction.system"),
                0.3,
            )
        except Exception as e:
            raise RuntimeError(
                "要望抽出: TEXT_LLM の呼び出しに失敗しました（modules.requirement_extractor.extract_requirements）。"
                f" 原因: {e}"
            ) from e

        if not (raw or "").strip():
            raise RuntimeError(
                "要望抽出: LLM の応答が空です（modules.requirement_extractor.extract_requirements）。"
            )

        stripped_head = raw.strip()
        if stripped_head.startswith("{"):
            # 後方互換: 旧プロンプトが JSON のみを返した場合
            data = _json_from_llm(raw)
            if not isinstance(data, dict):
                raise RuntimeError(
                    "要望抽出: JSON 開始 `{` があるがオブジェクトとしてパースできませんでした（modules.requirement_extractor）。"
                    f" 応答先頭: {(raw or '')[:500]!r}"
                )
            finalized = validate_requirements_result(
                data, expected=expected, max_pages=max_pages
            )
        else:
            plain = _unwrap_plaintext_llm_output(raw)
            finalized = _finalize_plain_prompt(
                plain,
                expected_plan_type=expected,
                max_pages=max_pages,
            )

        logger.info(
            "第1段（サイト制作プロンプト・テキスト）完了 plan_type=%s site_build_prompt_chars=%s",
            finalized.get("plan_type"),
            len((finalized.get("site_build_prompt") or "")),
        )
        return finalized
