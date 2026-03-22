"""TEXT_LLM パイプライン共通（プレーンテキスト正規化・要望 dict 整形・サイト台本から spec 組み立て・ technical_spec 付与）。"""
from __future__ import annotations

import logging
from typing import Any

import yaml
from config.config import get_common_technical_spec, get_contract_plan_info

from .llm_text_artifacts import requirements_dict_as_llm_fallback_text
from .site_script_parse import parse_llm_spec_or_site_script

logger = logging.getLogger(__name__)

MIN_SITE_BUILD_PROMPT_CHARS = 400


def require_gemini_text_llm(
    *,
    manual_flag: bool,
    api_key: str,
    plan_label: str,
    manual_env_name: str,
) -> None:
    """
    TEXT_LLM で Gemini マニュアルを使う前提を満たすことを要求する。
    ``manual_env_name`` はエラーメッセージ用（例: ``BASIC_CP_USE_GEMINI_MANUAL``）。
    """
    if manual_flag and (api_key or "").strip():
        return
    raise RuntimeError(
        f"{plan_label}: Gemini マニュアルが無効です。"
        f" {manual_env_name}=true かつ GEMINI_API_KEY を設定してください。"
    )

_SECTION_PLACEHOLDER = (
    "【サイト台本】このブロックはプレースホルダーです。上流工程の結合要望テキストを参照してください。"
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
            f"TEXT_LLM: 要望テキストが短すぎます（{len(stripped)} 文字）。"
            f"最低 {MIN_SITE_BUILD_PROMPT_CHARS} 文字以上必要です。"
            "（modules.llm.llm_pipeline_common.finalize_plain_prompt）"
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


def apply_common_technical_to_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """仕様 dict に共通 technical_spec を付与する。"""
    ts = spec.get("technical_spec")
    if isinstance(ts, dict):
        spec["technical_spec"] = _merge_common_technical_spec(ts)
    else:
        spec["technical_spec"] = _merge_common_technical_spec(None)
    return spec


def _build_site_script_markdown_yaml(
    *,
    partner_name: str,
    contract_plan: str,
    contract_pages: int,
    site_build_prompt_snippet: str,
) -> str:
    """Markdown + 末尾 ```yaml```（parse_llm_spec_or_site_script 互換）。"""
    paths = _paths_for_pages(contract_pages)
    lines = [
        "# サイト台本（結合要望に基づく骨子）",
        "",
        f"パートナー: {partner_name or '（未設定）'}。契約プラン: {contract_plan}。ページ数: {contract_pages}。",
    ]
    for p in paths:
        lines.append("")
        lines.append(f"## ページ: {p}")
        lines.append("")
        lines.append((_SECTION_PLACEHOLDER + "\n") * 8)
    snip = (site_build_prompt_snippet or "").strip()[:2000]
    if snip:
        lines.append("")
        lines.append("### マスタープロンプト（抜粋）")
        lines.append(snip)
    body = "\n".join(lines)

    site_nm = (partner_name or "").strip() or "サイト"
    meta: dict[str, Any] = {
        "site_overview": {
            "site_name": site_nm,
            "purpose": "契約プランと結合要望に基づくサイト構成",
            "target_users": "（要定義）",
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
            "design_principles": ["アクセシビリティ", "モバイルファースト"],
        },
        "content_spec": {},
        "page_structure": [
            {"path": p, "title": f"ページ{i}"} for i, p in enumerate(paths)
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
                "description": "メインビジュアル",
                "aspect_hint": "16:9",
            },
            {
                "page_path": "/",
                "section_id": "sub1",
                "description": "サブ画像1",
                "aspect_hint": "4:3",
            },
            {
                "page_path": "/",
                "section_id": "sub2",
                "description": "サブ画像2",
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


def assemble_spec_dict_from_requirements(
    requirements_result: dict[str, Any],
    contract_plan: str,
    partner_name: str,
) -> dict[str, Any]:
    """
    requirements_result の site_build_prompt（等）からサイト台本を組み、
    parse して仕様 dict（technical_spec マージ済み）を返す。
    STANDARD / ADVANCE の Gemini マニュアル後段などが利用する。
    """
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
            sbp = "【互換: 要約のみ】\n" + requirements_dict_as_llm_fallback_text(
                requirements_result
            )

    raw = _build_site_script_markdown_yaml(
        partner_name=partner_name,
        contract_plan=contract_plan,
        contract_pages=contract_pages,
        site_build_prompt_snippet=sbp,
    )
    try:
        data, mode = parse_llm_spec_or_site_script(raw)
    except ValueError as e:
        raise RuntimeError(
            "TEXT_LLM: 仕様のパースに失敗しました（modules.llm.llm_pipeline_common.assemble_spec_dict_from_requirements）。"
            f" 原因: {e}"
        ) from e

    if not isinstance(data, dict) or not data.get("site_overview"):
        raise RuntimeError(
            "TEXT_LLM: site_overview がありません（modules.llm.llm_pipeline_common.assemble_spec_dict_from_requirements）。"
        )

    if mode == "site_script":
        logger.info(
            "サイト台本を解釈しました（Markdown+YAML） site_script_chars=%s",
            len(data.get("site_script_md") or ""),
        )
    else:
        logger.info("レガシー仕様 JSON を解釈しました")
    return apply_common_technical_to_spec(data)
