"""仕様書に基づき技術土台へ Next.js ページ・セクションを LLM で実装する"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional
from config.config import (
    OUTPUT_DIR,
    SITE_BUILD_ENABLED,
    SITE_BUILD_MAX_FIX_ATTEMPTS,
    SITE_IMPLEMENTATION_ENABLED,
    get_contract_plan_info,
)
from config.prompt_settings import format_prompt, get_prompt_str, get_technical_spec_prompt_block
from modules.llm_output_files import parse_llm_file_blocks
from modules.site_build import _ensure_package_json, verify_site_build
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)

try:
    import yaml as _yaml_mod
except ImportError:  # pragma: no cover
    _yaml_mod = None

# 画像生成（from_placeholder_source）が TSX 内のタグを走査するための下限
_MIN_IMAGE_PLACEHOLDER_TAGS = 3


def count_image_placeholder_tags(site_dir: Path) -> int:
    """サイトディレクトリ内の .tsx における <ImagePlaceholder 出現数（自己閉じ・ペア両対応で先頭タグのみ数える）。"""
    n = 0
    for path in site_dir.rglob("*.tsx"):
        if "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        n += len(re.findall(r"<ImagePlaceholder\b", text))
    return n


# LLM が誤生成しやすく、lucide-react に存在しない export（ビルドで TS が落ちる）
_LUCIDE_BAD_ICON_NAMES: dict[str, str] = {
    "Pipe": "Droplets",
}


def patch_bad_lucide_icon_imports(site_dir: Path) -> int:
    """
    lucide-react の import / JSX で誤ったアイコン名を置換する。
    Returns:
        変更したファイル数
    """
    n = 0
    for path in list(site_dir.rglob("*.tsx")) + list(site_dir.rglob("*.ts")):
        if "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "lucide-react" not in text:
            continue
        new = text
        for old, repl in _LUCIDE_BAD_ICON_NAMES.items():
            new = re.sub(r"\b" + re.escape(old) + r"\b", repl, new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            logger.info("lucide 誤アイコン名を修復: %s", path.relative_to(site_dir))
            n += 1
    return n


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len // 2] + "\n\n...[truncated]...\n\n" + s[-max_len // 2 :]


def write_visual_style_brief(site_dir: Path, spec: dict) -> None:
    """
    画像生成パイプライン用。仕様書から一貫した画風指示を別コンテキストで使う。
    （サイト実装 LLM とは独立した JSON のみ共有）
    """
    docs = site_dir / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    overview = spec.get("site_overview") or {}
    design = spec.get("design_spec") or {}
    colors = design.get("color_scheme") or design.get("colors") or {}
    layout_mood = design.get("layout_mood") or design.get("layout_style", "")
    slots = spec.get("image_placeholder_slots") or []
    ref_desc: list[str] = []
    if isinstance(slots, list):
        for s in slots[:10]:
            if isinstance(s, dict):
                d = (s.get("description") or "").strip()
                if d:
                    ref_desc.append(d[:240])
    brief = {
        "version": 1,
        "site_name": overview.get("site_name", ""),
        "industry_or_purpose": overview.get("purpose", ""),
        "target_users": overview.get("target_users", ""),
        "layout_mood": layout_mood,
        "color_scheme": colors,
        "typography_hint": design.get("typography", {}),
        "image_consistency_rules": [
            "すべての生成画像で同一の写真・イラストスタイル（ライティング・彩度・構図の密度）を維持する",
            "画像内に文字・ロゴ・電話番号を描かない（Web上は HTML で表示する）",
            "実在企業の固有名・顔写真の特定は避ける",
            "不適切・誤解を招く表現を避ける",
        ],
    }
    if ref_desc:
        brief["reference_slot_descriptions"] = ref_desc
    path = docs / "visual_style_brief.json"
    path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("visual_style_brief.json を書き込みました: %s", path)


def write_image_pipeline_context(site_dir: Path, spec: dict) -> None:
    """
    画像工程が spec 引数なしで動くよう、第2段メタのみ site_dir に保存する。
    （site_script_md は含めない。巨大テキストの重複を避ける）
    """
    docs = site_dir / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    ctx = {
        "version": 1,
        "site_overview": spec.get("site_overview") or {},
        "design_spec": spec.get("design_spec") or {},
        "content_spec": spec.get("content_spec") or {},
        "image_placeholder_slots": spec.get("image_placeholder_slots") or [],
    }
    out = docs / "image_pipeline_context.json"
    out.write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("image_pipeline_context.json を書き込みました: %s", out)


def _spec_for_prompt(spec: dict) -> str:
    try:
        raw = json.dumps(spec, ensure_ascii=False)
    except (TypeError, ValueError):
        raw = str(spec)
    return _truncate(raw, 180_000)


def _design_tokens_block(design: Optional[Dict[str, Any]]) -> str:
    if not isinstance(design, dict) or not design:
        return "（design_spec なし）"
    if _yaml_mod is not None:
        try:
            return _yaml_mod.dump(
                design, allow_unicode=True, default_flow_style=False
            ).strip()
        except (TypeError, ValueError, AttributeError):
            pass
    return str(design)


def _implementation_brief(spec: dict) -> str:
    """第3段へ渡す単一ブロック（サイト台本ルート or レガシー JSON）。"""
    md = (spec.get("site_script_md") or "").strip()
    if md:
        if len(md) > 120_000:
            logger.warning(
                "サイト台本が長いため実装プロンプト用に %s 文字へ切り詰めます（元 %s）",
                120_000,
                len(md),
            )
            md = _truncate(md, 120_000)
        dt = _design_tokens_block(spec.get("design_spec") if isinstance(spec.get("design_spec"), dict) else {})
        return (
            "【サイト台本（Markdown・第2段の確定稿）】\n"
            "見出し順・各見出し直下の本文・FAQ・CTA はこれに従い、**意味を変えず**に UI に落とすこと。\n\n"
            f"{md}\n\n"
            "【デザイントークン（コードに忠実に反映。body 全面ベタ塗りの強彩度は禁止）】\n"
            f"{dt}"
        )
    return "【仕様書 JSON（レガシールート）】\n" + _spec_for_prompt(spec)


class SiteImplementer:
    """仕様書 + 技術要件から TSX を生成し、ビルドが通るまで修正を試みる"""

    def __init__(self) -> None:
        pass

    def is_configured(self) -> bool:
        return is_text_llm_configured()

    def implement(self, spec: dict, site_dir: Path, contract_plan: str = "") -> tuple[bool, str]:
        """
        Returns:
            (成功, 最後のビルドログまたはメッセージ)
        """
        if not SITE_IMPLEMENTATION_ENABLED:
            logger.info("SITE_IMPLEMENTATION_ENABLED=false のためスキップ")
            return True, "skipped"

        site_dir = site_dir.resolve()
        output_root = OUTPUT_DIR.resolve()
        try:
            site_dir.relative_to(output_root)
        except ValueError as e:
            raise ValueError(
                f"site_dir は OUTPUT_DIR 配下である必要があります: {output_root}"
            ) from e

        if not self.is_configured():
            logger.error(
                "サイト実装用のテキスト LLM が未設定です。"
                "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
            )
            return False, "no_llm_credentials"

        write_visual_style_brief(site_dir, spec)
        write_image_pipeline_context(site_dir, spec)
        plan_info = get_contract_plan_info(contract_plan or "")
        max_pages = max(1, int(plan_info.get("pages") or 1))

        base_prompt = self._build_implementation_prompt(spec, max_pages)
        messages_for_log: list[str] = []
        last_build_log = ""
        no_parse_snippet = ""

        for attempt in range(SITE_BUILD_MAX_FIX_ATTEMPTS):
            if attempt == 0:
                user_content = base_prompt
            else:
                parse_failure_hint = ""
                if no_parse_snippet:
                    parse_failure_hint = (
                        "### 前回: ファイルブロックが 0 件でした（パース不能）\n"
                        "説明文・JSON だけ・コードフェンスにパス行が無い形式は無効です。"
                        "**今すぐ** `<<<FILE app/page.tsx>>>` から始め `<<<ENDFILE>>>` で閉じるか、"
                        "`<file path=\"app/page.tsx\">` ... `</file>` か、行頭 ```tsx app/page.tsx の形式で全文を出し直してください。\n\n"
                        "#### 前回応答の先頭（参考）\n```\n"
                        + _truncate(no_parse_snippet, 8_000)
                        + "\n```\n"
                    )
                user_content = format_prompt(
                    "site_implementation.fix_user_template",
                    build_log=_truncate(last_build_log or "（ビルド未実行）", 14_000),
                    parse_failure_hint=parse_failure_hint,
                )

            text = self._call_llm(user_content, is_fix=(attempt > 0))
            if not text:
                messages_for_log.append("empty_llm_response")
                no_parse_snippet = "(LLM 応答が空)"
                continue

            files_written = self._apply_files(site_dir, text)
            if not files_written:
                no_parse_snippet = text.strip()
                logger.warning(
                    "パース可能な FILE ブロックがありませんでした（試行 %s）。応答先頭 600 文字: %r",
                    attempt + 1,
                    (text or "")[:600],
                )
                messages_for_log.append("no_file_blocks")
                continue

            no_parse_snippet = ""

            # LLM が app/components/lib のみ出力してもルートの package.json は残る想定。
            # 欠落時はテンプレから復元（npm install の ENOENT 防止）。
            _ensure_package_json(site_dir)

            patched = patch_bad_lucide_icon_imports(site_dir)
            if patched:
                logger.info("lucide 誤名パッチ適用: %s ファイル", patched)

            if not SITE_BUILD_ENABLED:
                logger.info("SITE_BUILD_ENABLED=false のためビルド検証をスキップ")
                return True, "build_skipped"

            ph_n = count_image_placeholder_tags(site_dir)
            if ph_n < _MIN_IMAGE_PLACEHOLDER_TAGS:
                last_build_log = (
                    f"[前提チェック] `<ImagePlaceholder />` が {ph_n} 箇所のみです。"
                    f"画像生成パイプライン用に最低 {_MIN_IMAGE_PLACEHOLDER_TAGS} 箇所以上必要です。"
                    "各ページのヒーローに 1 つ、サービス・実績・会社・採用などにあわせて追加してください。"
                    "`import ImagePlaceholder from \"@/components/ImagePlaceholder\"` と "
                    "`description=\"...\"` `aspectClassName=\"aspect-video\"` 等を付与。"
                    "（この時点では npm run build は未実行）"
                )
                logger.warning(
                    "ImagePlaceholder 不足 (%s / 最低 %s) — 修正ラウンドへ",
                    ph_n,
                    _MIN_IMAGE_PLACEHOLDER_TAGS,
                )
                continue

            ok, last_build_log = verify_site_build(
                site_dir, skip_install=(attempt > 0)
            )
            if ok:
                logger.info("サイト実装 + ビルド成功（試行 %s）", attempt + 1)
                return True, last_build_log

            logger.warning("ビルド失敗、修正試行 %s / %s", attempt + 1, SITE_BUILD_MAX_FIX_ATTEMPTS)

        # last_build_log が空のままだと main 側に「build_failed」しか出ず原因特定不能。
        # （LLM 空応答・FILE ブロック0件のループで npm 未到達のときなど）
        detail = (last_build_log or "").strip()
        if not detail:
            parts: list[str] = []
            if messages_for_log:
                parts.append(
                    "試行サマリ: " + ", ".join(messages_for_log)
                )
            if no_parse_snippet and no_parse_snippet.strip():
                parts.append(
                    "直近の非ファイル応答先頭:\n"
                    + _truncate(no_parse_snippet.strip(), 1_200)
                )
            if parts:
                detail = (
                    "[サイト実装] npm ログは未取得（ビルド前に失敗した可能性）。"
                    + "\n\n".join(parts)
                )
            else:
                detail = (
                    "[サイト実装] 詳細ログなし。"
                    " TEXT_LLM の応答が空、またはパース可能なファイルブロックが一度も無かった可能性。"
                    " CURSOR_AGENT_COMMAND / タイムアウト / CLI ログを確認してください。"
                )
        return False, detail

    def _call_llm(self, user_content: str, is_fix: bool) -> str:
        system = get_prompt_str("site_implementation.system").strip()
        try:
            return text_llm_complete(
                user=user_content,
                system=system,
                temperature=0.2 if is_fix else 0.35,
                max_tokens=16_384,
            )
        except Exception as e:
            logger.error("サイト実装 LLM エラー: %s", e, exc_info=True)
        return ""

    def _build_implementation_prompt(self, spec: dict, max_pages: int) -> str:
        tech = get_technical_spec_prompt_block()

        if max_pages <= 1:
            multi_hint = get_prompt_str("site_implementation.single_page_hint")
        else:
            multi_hint = format_prompt(
                "site_implementation.multi_page_hint_template",
                max_pages=str(max_pages),
            )

        return format_prompt(
            "site_implementation.user_template",
            tech=tech,
            multi_hint=multi_hint,
            implementation_brief=_implementation_brief(spec),
        )

    def _apply_files(self, site_dir: Path, llm_text: str) -> int:
        blocks = parse_llm_file_blocks(llm_text)
        n = 0
        base = site_dir.resolve()
        for rel, content in blocks.items():
            path = (base / rel).resolve()
            try:
                path.relative_to(base)
            except ValueError:
                logger.error("パストラバーサル疑いのためスキップ: %s", rel)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
            n += 1
            logger.info("書き込み: %s", rel)
        return n
