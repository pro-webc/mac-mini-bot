"""BASIC LP（1ページランディング）契約向け TEXT_LLM 工程。

実 Gemini チェーンを接続する際も、このモジュールに集約する。
現状はモック（ヒアリング転記 + LP 向け仕様スタブ）。
"""
from __future__ import annotations

import json
import logging
from typing import Any

import yaml
from config.config import get_contract_plan_info

from modules.llm_mock import (
    MIN_SITE_BUILD_PROMPT_CHARS,
    apply_common_technical_to_spec,
    finalize_plain_prompt,
)
from modules.site_script_parse import parse_llm_spec_or_site_script

logger = logging.getLogger(__name__)

_FILLER_LINE = (
    "【BASIC LP モック】実運用では Gemini 多段プロンプトの出力に置き換える。"
)


def build_basic_lp_site_build_prompt(
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
) -> str:
    """BASIC LP 向けマスタープロンプト相当テキスト（最低文字数を満たす）。"""
    chunks = [
        "【BASIC LP / TEXT_LLM】契約プラン BASIC LP（1ページランディング）。",
        "コンバージョン導線・ファーストビュー・信頼要素を1画面に集約する前提。",
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
        pad_n = (
            (MIN_SITE_BUILD_PROMPT_CHARS - len(body)) // max(len(_FILLER_LINE), 1) + 2
        )
        body = body + "\n\n" + "\n".join([_FILLER_LINE] * pad_n)
    return body


def build_basic_lp_spec_raw(
    *,
    partner_name: str,
    contract_plan: str,
    site_build_prompt_snippet: str,
) -> str:
    """Markdown + 末尾 ```yaml```（parse_llm_spec_or_site_script 互換・1ページ固定）。"""
    lines = [
        "# BASIC LP サイト台本（1ページ）",
        "",
        f"パートナー: {partner_name or '（未設定）'}。契約: {contract_plan}（ランディング・単一 URL）。",
        "ヒーロー → 課題・解決 → 実績または信頼 → 料金・FAQ（任意）→ お問い合わせ など、スクロール1本の流れを想定。",
        "",
        "## ページ: /",
        "",
        *[_FILLER_LINE + "\n" for _ in range(8)],
    ]
    snip = (site_build_prompt_snippet or "").strip()[:2000]
    if snip:
        lines.extend(["", "### マスタープロンプト（抜粋）", snip])
    body = "\n".join(lines)

    site_nm = (partner_name or "").strip() or "ランディング"
    meta: dict[str, Any] = {
        "site_overview": {
            "site_name": site_nm,
            "purpose": "BASIC LP（1ページ）によるリード獲得・問い合わせ転換",
            "target_users": "ヒアリングで定義された見込み顧客",
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
            "layout_mood": "ランディング・情報密度は中程度・余白で可読性",
            "design_principles": [
                "シングルページ",
                "CTA の視認性",
                "モバイルファースト",
            ],
        },
        "content_spec": {},
        "page_structure": [{"path": "/", "title": "ランディング"}],
        "ux_spec": {
            "primary_conversion": {"label": "お問い合わせ", "action": "#contact"},
            "secondary_actions": [],
            "navigation_model": "シングルページ（アンカーリンク）",
            "trust_placement": "中盤〜フッター直前",
            "mobile_notes": "タップ領域 44px 以上・固定ヘッダーは薄く",
        },
        "function_spec": {},
        "image_placeholder_slots": [
            {
                "page_path": "/",
                "section_id": "hero",
                "description": "ヒーロー・メインビジュアル",
                "aspect_hint": "16:9",
            },
            {
                "page_path": "/",
                "section_id": "proof",
                "description": "実績・導入事例・ロゴ帯（任意）",
                "aspect_hint": "16:9",
            },
            {
                "page_path": "/",
                "section_id": "closing",
                "description": "クロージング前の補助画像（任意）",
                "aspect_hint": "4:3",
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


def build_basic_lp_requirements_result(
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
) -> dict[str, Any]:
    """要望抽出相当（plan_type=basic_lp・ページ数1）。"""
    plan_info = get_contract_plan_info(contract_plan)
    max_pages = int(plan_info.get("pages") or 1)
    plain = build_basic_lp_site_build_prompt(
        hearing_sheet_content,
        appo_memo,
        sales_notes,
    )
    return finalize_plain_prompt(
        plain,
        expected_plan_type="basic_lp",
        max_pages=max_pages,
    )


def build_basic_lp_spec_dict(
    requirements_result: dict[str, Any],
    contract_plan: str,
    partner_name: str,
) -> dict[str, Any]:
    """仕様 dict（technical_spec マージ済み）。"""
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

    raw = build_basic_lp_spec_raw(
        partner_name=partner_name,
        contract_plan=contract_plan,
        site_build_prompt_snippet=sbp,
    )
    try:
        data, mode = parse_llm_spec_or_site_script(raw)
    except ValueError as e:
        raise RuntimeError(
            "BASIC LP TEXT_LLM: 仕様のパースに失敗しました（modules.basic_lp_text_llm）。"
            f" 原因: {e}"
        ) from e

    if not isinstance(data, dict) or not data.get("site_overview"):
        raise RuntimeError(
            "BASIC LP TEXT_LLM: site_overview がありません（modules.basic_lp_text_llm）。"
        )

    if mode == "site_script":
        logger.info(
            "BASIC LP TEXT_LLM: サイト台本（Markdown+YAML） site_script_chars=%s",
            len(data.get("site_script_md") or ""),
        )
    else:
        logger.info("BASIC LP TEXT_LLM: レガシー仕様 JSON を解釈しました")
    return apply_common_technical_to_spec(data)


def run_basic_lp_text_llm_pipeline(
    *,
    hearing_sheet_content: str,
    appo_memo: str,
    sales_notes: str,
    contract_plan: str,
    partner_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    BASIC LP 向け要望整理 + 仕様生成。

    - ``BASIC_LP_USE_GEMINI_MANUAL=true`` かつ ``GEMINI_API_KEY`` あり: マニュアル手順の Gemini チェーン
    - それ以外: モック

    Returns:
        (requirements_result, spec)
    """
    from config.config import BASIC_LP_USE_GEMINI_MANUAL, GEMINI_API_KEY

    if BASIC_LP_USE_GEMINI_MANUAL and (GEMINI_API_KEY or "").strip():
        from modules.basic_lp_gemini_manual import run_basic_lp_gemini_manual_pipeline

        requirements_result, spec, _ = run_basic_lp_gemini_manual_pipeline(
            hearing_sheet_content=hearing_sheet_content,
            appo_memo=appo_memo,
            sales_notes=sales_notes,
            contract_plan=contract_plan,
            partner_name=partner_name,
        )
        logger.info(
            "BASIC LP TEXT_LLM（Gemini マニュアル）完了 plan_type=%s site_build_prompt_chars=%s",
            requirements_result.get("plan_type"),
            len(requirements_result.get("site_build_prompt") or ""),
        )
        return requirements_result, spec

    requirements_result = build_basic_lp_requirements_result(
        hearing_sheet_content,
        appo_memo,
        sales_notes,
        contract_plan,
    )
    spec = build_basic_lp_spec_dict(
        requirements_result,
        contract_plan,
        partner_name,
    )
    logger.info(
        "BASIC LP TEXT_LLM（モック）完了 plan_type=%s site_build_prompt_chars=%s pages=1",
        requirements_result.get("plan_type"),
        len(requirements_result.get("site_build_prompt") or ""),
    )
    return requirements_result, spec
