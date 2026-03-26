"""BASIC LP（1ページランディング）向け: マニュアル後の要望からサイト台本・仕様 dict を組み立てる。

``basic_lp_claude_manual`` が ``build_basic_lp_spec_dict`` を参照する。TEXT_LLM の入口は
``text_llm_stage.run_text_llm_stage`` のみ。
"""
from __future__ import annotations

import logging
from typing import Any

import yaml

from .llm_pipeline_common import apply_common_technical_to_spec
from .llm_text_artifacts import requirements_dict_as_llm_fallback_text
from .site_script_parse import parse_llm_spec_or_site_script

logger = logging.getLogger(__name__)

_SECTION_PLACEHOLDER = (
    "【サイト台本】セクション本文プレースホルダー（Claude マニュアル結合要望で上書きされる想定）。"
)


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
        *[_SECTION_PLACEHOLDER + "\n" for _ in range(8)],
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
            sbp = "【互換: 要約のみ】\n" + requirements_dict_as_llm_fallback_text(
                requirements_result
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
            "BASIC LP TEXT_LLM: 仕様のパースに失敗しました（modules.llm.basic_lp_spec）。"
            f" 原因: {e}"
        ) from e

    if not isinstance(data, dict) or not data.get("site_overview"):
        raise RuntimeError(
            "BASIC LP TEXT_LLM: site_overview がありません（modules.llm.basic_lp_spec）。"
        )

    if mode == "site_script":
        logger.info(
            "BASIC LP TEXT_LLM: サイト台本（Markdown+YAML） site_script_chars=%s",
            len(data.get("site_script_md") or ""),
        )
    else:
        logger.info("BASIC LP TEXT_LLM: レガシー仕様 JSON を解釈しました")
    return apply_common_technical_to_spec(data)
