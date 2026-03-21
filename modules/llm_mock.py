"""モック TEXT_LLM: 要望抽出と仕様生成を同一工程として扱う（外部 API / CLI 不使用）。"""
from __future__ import annotations

import json
import logging
from typing import Any

import yaml
from config.config import get_common_technical_spec, get_contract_plan_info

from modules.contract_workflow import ContractWorkBranch
from modules.site_script_parse import parse_llm_spec_or_site_script

logger = logging.getLogger(__name__)

MIN_SITE_BUILD_PROMPT_CHARS = 400

_FILLER_LINE = (
    "モック用の固定コピー。実運用では TEXT_LLM 出力に置き換える。"
)

_DEFAULT_PATHS = ["/", "/about", "/services", "/works", "/company", "/contact"]


def unwrap_plaintext_llm_output(text: str) -> str:
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


def expected_plan_type(plan_info: dict) -> str:
    """契約プランから、抽出結果に期待する plan_type。"""
    if plan_info.get("type") == "landing_page":
        return "basic_lp"
    if plan_info.get("name") == "BASIC" and plan_info.get("pages") == 1:
        return "basic"
    if plan_info.get("type") == "website" and int(plan_info.get("pages") or 0) > 1:
        name = (plan_info.get("name") or "").upper()
        return "advance" if name == "ADVANCE" else "standard"
    return "general"


def finalize_plain_prompt(
    site_build_prompt: str,
    *,
    expected_plan_type: str,
    max_pages: int,
) -> dict[str, Any]:
    """site_build_prompt を requirements_result 形に正規化する。"""
    stripped = site_build_prompt.strip()
    if len(stripped) < MIN_SITE_BUILD_PROMPT_CHARS:
        raise RuntimeError(
            f"モック TEXT_LLM: 要望テキストが短すぎます（{len(stripped)} 文字）。"
            f"最低 {MIN_SITE_BUILD_PROMPT_CHARS} 文字以上必要です。"
            " modules.llm_mock.finalize_plain_prompt"
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


def _paths_for_pages(n: int) -> list[str]:
    n = max(1, int(n))
    if n == 1:
        return ["/"]
    return _DEFAULT_PATHS[: min(n, len(_DEFAULT_PATHS))]


def build_mock_site_build_prompt(
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
) -> str:
    """入力を転記し、最低文字数を満たすマスタープロンプト相当テキスト。"""
    chunks = [
        "【モック TEXT_LLM】スプレッドシート入力を転記した開発用スタブです。",
        "",
        "【ヒアリング原文】",
        (hearing_sheet_content or "").strip()[:12000],
        "",
        "【アポメモ】",
        (appo_memo or "").strip()[:8000],
        "",
        "【営業メモ】",
        (sales_notes or "").strip()[:8000],
    ]
    body = "\n".join(chunks).strip()
    if len(body) < MIN_SITE_BUILD_PROMPT_CHARS:
        pad_n = (MIN_SITE_BUILD_PROMPT_CHARS - len(body)) // max(len(_FILLER_LINE), 1) + 2
        body = body + "\n\n" + "\n".join([_FILLER_LINE] * pad_n)
    return body


def build_mock_spec_raw(
    *,
    partner_name: str,
    contract_plan: str,
    contract_pages: int,
    site_build_prompt_snippet: str,
) -> str:
    """Markdown + 末尾 ```yaml```（parse_llm_spec_or_site_script 互換）。"""
    paths = _paths_for_pages(contract_pages)
    lines = [
        "# モックサイト台本",
        "",
        f"パートナー: {partner_name or '（未設定）'}。契約プラン: {contract_plan}。ページ数: {contract_pages}。",
        "本文は CI・ローカル検証用の固定文言です。",
    ]
    for p in paths:
        lines.append("")
        lines.append(f"## ページ: {p}")
        lines.append("")
        lines.append((_FILLER_LINE + "\n") * 8)
    snip = (site_build_prompt_snippet or "").strip()[:2000]
    if snip:
        lines.append("")
        lines.append("### マスタープロンプト（抜粋）")
        lines.append(snip)
    body = "\n".join(lines)

    site_nm = (partner_name or "").strip() or "モックサイト"
    meta: dict[str, Any] = {
        "site_overview": {
            "site_name": site_nm,
            "purpose": "モック（TEXT_LLM オフ）による検証用サイト",
            "target_users": "開発・自動テスト",
        },
        "design_spec": {
            "color_scheme": {
                "background": "#fafaf9",
                "primary": "#0f766e",
                "text": "#0f172a",
                "border": "#e2e8f0",
                "primary_foreground": "#ffffff",
            },
            "typography": {},
            "layout_mood": "フラット・可読性優先",
            "design_principles": ["モック", "アクセシビリティ"],
        },
        "content_spec": {},
        "page_structure": [
            {"path": p, "title": f"モック{i}"} for i, p in enumerate(paths)
        ],
        "ux_spec": {
            "primary_conversion": {"label": "お問い合わせ", "action": "/contact"},
            "secondary_actions": [],
            "navigation_model": "シンプルナビ",
            "trust_placement": "フッター付近",
            "mobile_notes": "タップ領域 44px 以上",
        },
        "function_spec": {},
        "image_placeholder_slots": [
            {
                "page_path": "/",
                "section_id": "hero",
                "description": "モック・メインビジュアル",
                "aspect_hint": "16:9",
            },
            {
                "page_path": "/",
                "section_id": "sub1",
                "description": "モック・サブ画像1",
                "aspect_hint": "4:3",
            },
            {
                "page_path": "/",
                "section_id": "sub2",
                "description": "モック・サブ画像2",
                "aspect_hint": "16:9",
            },
        ],
    }
    yaml_text = yaml.safe_dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    return f"{body}\n\n```yaml\n{yaml_text.strip()}\n```\n"


def _merge_common_technical_spec(extra: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if extra:
        merged.update(extra)
    merged["tech_stack"] = [
        "Next.js (App Router)",
        "React",
        "TypeScript",
        "Tailwind CSS",
    ]
    merged["common_requirements"] = get_common_technical_spec()
    return merged


def _apply_common_technical_to_spec(spec: dict[str, Any]) -> dict[str, Any]:
    ts = spec.get("technical_spec")
    if isinstance(ts, dict):
        spec["technical_spec"] = _merge_common_technical_spec(ts)
    else:
        spec["technical_spec"] = _merge_common_technical_spec(None)
    return spec


def apply_common_technical_to_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """仕様 dict に共通 technical_spec を付与する（プラン別パイプラインから利用）。"""
    return _apply_common_technical_to_spec(spec)


def build_requirements_result_mock(
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
) -> dict[str, Any]:
    """要望抽出相当の dict を生成する。"""
    plan_info = get_contract_plan_info(contract_plan)
    expected = expected_plan_type(plan_info)
    max_pages = int(plan_info.get("pages") or 1)
    plain = build_mock_site_build_prompt(
        hearing_sheet_content,
        appo_memo,
        sales_notes,
    )
    return finalize_plain_prompt(
        plain,
        expected_plan_type=expected,
        max_pages=max_pages,
    )


def build_spec_dict_mock(
    hearing_sheet_content: str,
    requirements_result: dict[str, Any],
    contract_plan: str,
    partner_name: str,
) -> dict[str, Any]:
    """仕様書 dict（technical_spec マージ済み）を生成する。"""
    plan_info = get_contract_plan_info(contract_plan)
    contract_pages = int(plan_info.get("pages") or 1)
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

    raw = build_mock_spec_raw(
        partner_name=partner_name,
        contract_plan=contract_plan,
        contract_pages=contract_pages,
        site_build_prompt_snippet=sbp,
    )
    try:
        data, mode = parse_llm_spec_or_site_script(raw)
    except ValueError as e:
        raise RuntimeError(
            "モック TEXT_LLM: 仕様のパースに失敗しました（modules.llm_mock.build_spec_dict_mock）。"
            f" 原因: {e}"
        ) from e

    if not isinstance(data, dict) or not data.get("site_overview"):
        raise RuntimeError(
            "モック TEXT_LLM: site_overview がありません（modules.llm_mock.build_spec_dict_mock）。"
        )

    if mode == "site_script":
        logger.info(
            "モック TEXT_LLM: サイト台本（Markdown+YAML） site_script_chars=%s",
            len(data.get("site_script_md") or ""),
        )
    else:
        logger.info("モック TEXT_LLM: レガシー仕様 JSON を解釈しました")
    return apply_common_technical_to_spec(data)


def run_mock_text_llm_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
    work_branch: ContractWorkBranch,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    要望抽出と仕様生成を **1 工程のモック TEXT_LLM** として実行する。

    Args:
        work_branch: 契約プラン由来の作業分岐（実 LLM チェーンの分岐と揃える）。

    Returns:
        (requirements_result, spec)
    """
    requirements_result = build_requirements_result_mock(
        hearing_sheet_content,
        appo_memo,
        sales_notes,
        contract_plan,
    )
    spec = build_spec_dict_mock(
        hearing_sheet_content,
        requirements_result,
        contract_plan,
        partner_name,
    )
    logger.info(
        "モック TEXT_LLM 工程完了 work_branch=%s plan_type=%s site_build_prompt_chars=%s",
        work_branch.value,
        requirements_result.get("plan_type"),
        len(requirements_result.get("site_build_prompt") or ""),
    )
    return requirements_result, spec
