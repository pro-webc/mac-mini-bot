"""仕様書に基づき技術土台へ Next.js ページ・セクションを LLM で実装する"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from config.config import (
    OUTPUT_DIR,
    SITE_BUILD_ENABLED,
    SITE_BUILD_MAX_FIX_ATTEMPTS,
    SITE_IMPLEMENTATION_ENABLED,
    get_common_technical_spec_prompt_block,
    get_contract_plan_info,
)
from modules.llm_output_files import parse_llm_file_blocks
from modules.site_build import verify_site_build
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)


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
    brief = {
        "version": 1,
        "site_name": overview.get("site_name", ""),
        "industry_or_purpose": overview.get("purpose", ""),
        "target_users": overview.get("target_users", ""),
        "layout_mood": design.get("layout_style", ""),
        "color_scheme": colors,
        "typography_hint": design.get("typography", {}),
        "image_consistency_rules": [
            "すべての生成画像で同一の写真・イラストスタイル（ライティング・彩度・構図の密度）を維持する",
            "画像内に文字・ロゴ・電話番号を描かない（Web上は HTML で表示する）",
            "実在企業の固有名・顔写真の特定は避ける",
            "不適切・誤解を招く表現を避ける",
        ],
    }
    path = docs / "visual_style_brief.json"
    path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("visual_style_brief.json を書き込みました: %s", path)


def _spec_for_prompt(spec: dict) -> str:
    try:
        raw = json.dumps(spec, ensure_ascii=False)
    except (TypeError, ValueError):
        raw = str(spec)
    return _truncate(raw, 180_000)


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
        plan_info = get_contract_plan_info(contract_plan or "")
        max_pages = max(1, int(plan_info.get("pages") or 1))

        base_prompt = self._build_implementation_prompt(spec, max_pages)
        messages_for_log: list[str] = []
        last_build_log = ""

        for attempt in range(SITE_BUILD_MAX_FIX_ATTEMPTS):
            if attempt == 0:
                user_content = base_prompt
            else:
                user_content = f"""直前の実装で `npm run build` が失敗しました。次のログを解消するよう、該当ファイルだけを最小限修正してください。
同じ <<<FILE ...>>> 形式で、変更が必要なファイルのみ全文を出力してください。
TypeScript で「lucide-react に export がない」と出たら、該当 import を lucide.dev に実在するアイコン名に差し替え（例: `Pipe` は使えない → `Droplets` 等）。

--- build / typecheck log (truncated) ---
{_truncate(last_build_log, 14_000)}
"""

            text = self._call_llm(user_content, is_fix=(attempt > 0))
            if not text:
                messages_for_log.append("empty_llm_response")
                continue

            files_written = self._apply_files(site_dir, text)
            if not files_written:
                logger.warning("パース可能な FILE ブロックがありませんでした（試行 %s）", attempt + 1)
                messages_for_log.append("no_file_blocks")
                continue

            patched = patch_bad_lucide_icon_imports(site_dir)
            if patched:
                logger.info("lucide 誤名パッチ適用: %s ファイル", patched)

            if not SITE_BUILD_ENABLED:
                logger.info("SITE_BUILD_ENABLED=false のためビルド検証をスキップ")
                return True, "build_skipped"

            ok, last_build_log = verify_site_build(
                site_dir, skip_install=(attempt > 0)
            )
            if ok:
                logger.info("サイト実装 + ビルド成功（試行 %s）", attempt + 1)
                return True, last_build_log

            logger.warning("ビルド失敗、修正試行 %s / %s", attempt + 1, SITE_BUILD_MAX_FIX_ATTEMPTS)

        return False, last_build_log or "build_failed"

    def _call_llm(self, user_content: str, is_fix: bool) -> str:
        system = (
            "あなたは Next.js 14 App Router + TypeScript + Tailwind のシニアエンジニアです。"
            "指定のマーカー形式でのみファイルを出力し、説明文は最小限にしてください。"
        )
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
        spec_blob = _spec_for_prompt(spec)
        tech = get_common_technical_spec_prompt_block()

        multi_hint = ""
        if max_pages > 1:
            multi_hint = f"""
【ページ数】契約上最大 {max_pages} ページまで。
`page_structure` に基づき `app/<segment>/page.tsx` を作成すること（各ルートに page.tsx）。
トップ `app/page.tsx` から主要ページへのリンクを設置。
"""

        return f"""
以下の仕様書 JSON に従い、Next.js サイトの **実装コードのみ** を出力してください。

{tech}

【厳守】
- `app/page.tsx` / `app/layout.tsx` で import するコンポーネントは、**同じ応答内で** それぞれ `<<<FILE>>>` として必ず全文を出力すること（1つでも欠けるとビルド前に不足ファイルの stub が自動挿入され、未完成のままになる）
- 既存の `components/ImagePlaceholder.tsx` と `GoogleMapEmbed.tsx` を import して使用可能
- Unsplash・外部ストック URL・実ファイル画像は使わない。画像箇所は ImagePlaceholder（`description="..."` をダブルクォートで明示し、overlayText で必要なら重ね字の意図を明示。生成後に `public/images/generated/` の画像へ差し替えられる）
- 図表は HTML + Tailwind でマークアップ
- アイコンは lucide-react または react-icons（Simple Icons）。lucide は https://lucide.dev/icons にある名前のみ。`Pipe` は export されない（`Droplets` / `Wrench` / `Cable` 等に置き換え）
- box-shadow を Tailwind で使わない
- globals.css は変更しない（必要なら app/layout.tsx の className のみ）
- `<<<FILE 相対パス>>>` と `<<<ENDFILE>>>` で囲み、**app/** または **components/** 下のみ。1 ブロック = ファイル全文

【最低限含めるファイル】
- app/page.tsx（トップ）
- app/layout.tsx（metadata.title / description を仕様のサイト名・概要で更新）
- components/sections/ 以下にセクションを分割（1 セクション 1 コンポーネント）

{multi_hint}

【仕様書 JSON】
{spec_blob}
"""

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
