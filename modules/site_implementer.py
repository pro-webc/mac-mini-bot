"""仕様書メタをサイトに書き込み、テンプレ土台のままビルド検証する（LLM によるコード生成は行わない）。"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from config.config import OUTPUT_DIR, SITE_BUILD_ENABLED, SITE_IMPLEMENTATION_ENABLED

from modules.site_build import _ensure_package_json, verify_site_build

logger = logging.getLogger(__name__)

# 画像生成（from_placeholder_source）が TSX 内のタグを走査するための下限
_MIN_IMAGE_PLACEHOLDER_TAGS = 3

_MOCK_PLACEHOLDER_TSX = '''import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function MockLlmPlaceholders() {
  return (
    <div className="hidden" aria-hidden>
      <ImagePlaceholder description="mock-pipeline-1" aspectClassName="aspect-video" />
      <ImagePlaceholder description="mock-pipeline-2" aspectClassName="aspect-video" />
      <ImagePlaceholder description="mock-pipeline-3" aspectClassName="aspect-video" />
    </div>
  );
}
'''


def ensure_mock_image_placeholders(site_dir: Path) -> None:
    """テンプレ単体では ImagePlaceholder が不足しがちなため、非表示のモックを差し込む。"""
    comp = site_dir / "components" / "MockLlmPlaceholders.tsx"
    comp.parent.mkdir(parents=True, exist_ok=True)
    comp.write_text(_MOCK_PLACEHOLDER_TSX, encoding="utf-8")
    layout_path = site_dir / "app" / "layout.tsx"
    if not layout_path.is_file():
        return
    text = layout_path.read_text(encoding="utf-8")
    if "MockLlmPlaceholders" in text:
        return
    marker = 'import SiteFooter from "@/components/SiteFooter";'
    if marker not in text:
        logger.warning(
            "layout.tsx の import パターンが想定外のため MockLlmPlaceholders を差し込めませんでした"
        )
        return
    text = text.replace(
        marker,
        marker + '\nimport MockLlmPlaceholders from "@/components/MockLlmPlaceholders";',
        1,
    )
    text = text.replace(
        "<SiteFooter />",
        "<MockLlmPlaceholders />\n        <SiteFooter />",
        1,
    )
    layout_path.write_text(text, encoding="utf-8")


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


def write_visual_style_brief(site_dir: Path, spec: dict) -> None:
    """
    画像生成パイプライン用。仕様書から一貫した画風指示を別コンテキストで使う。
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


class SiteImplementer:
    """仕様メタの書き込みとテンプレ土台のビルド検証（モック・LLM 不使用）。"""

    def __init__(self) -> None:
        pass

    def is_configured(self) -> bool:
        return True

    def implement(self, spec: dict, site_dir: Path, contract_plan: str = "") -> tuple[bool, str]:
        """
        Returns:
            (成功, 最後のビルドログまたはメッセージ)
        """
        _ = contract_plan
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

        write_visual_style_brief(site_dir, spec)
        write_image_pipeline_context(site_dir, spec)
        ensure_mock_image_placeholders(site_dir)

        _ensure_package_json(site_dir)
        patched = patch_bad_lucide_icon_imports(site_dir)
        if patched:
            logger.info("lucide 誤名パッチ適用: %s ファイル", patched)

        if not SITE_BUILD_ENABLED:
            logger.info("SITE_BUILD_ENABLED=false のためビルド検証をスキップ")
            return True, "build_skipped"

        ph_n = count_image_placeholder_tags(site_dir)
        if ph_n < _MIN_IMAGE_PLACEHOLDER_TAGS:
            msg = (
                f"[サイト実装・モック] `<ImagePlaceholder />` が {ph_n} 箇所のみです（最低 "
                f"{_MIN_IMAGE_PLACEHOLDER_TAGS}）。layout への差し込みを確認してください。"
            )
            logger.error(msg)
            return False, msg

        ok, blog = verify_site_build(site_dir, skip_install=False)
        if ok:
            logger.info("サイト実装（モック）+ ビルド成功")
            return True, blog or ""
        return False, blog or ""
