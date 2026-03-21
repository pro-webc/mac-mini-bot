"""仕様書メタをサイトに書き込み、テンプレ土台のままビルド検証する（LLM によるコード生成は行わない）。"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from config.config import OUTPUT_DIR, SITE_BUILD_ENABLED, SITE_IMPLEMENTATION_ENABLED

from modules.site_build import _ensure_package_json, verify_site_build

logger = logging.getLogger(__name__)


_LUCIDE_BAD_ICON_NAMES: dict[str, str] = {
    "Pipe": "Droplets",
}


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

        _ensure_package_json(site_dir)
        patched = patch_bad_lucide_icon_imports(site_dir)
        if patched:
            logger.info("lucide 誤名パッチ適用: %s ファイル", patched)

        if not SITE_BUILD_ENABLED:
            logger.info("SITE_BUILD_ENABLED=false のためビルド検証をスキップ")
            return True, "build_skipped"

        ok, blog = verify_site_build(site_dir, skip_install=False)
        if ok:
            logger.info("サイト実装（モック）+ ビルド成功")
            return True, blog or ""
        return False, blog or ""
