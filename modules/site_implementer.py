"""サイトディレクトリのビルド検証（ソースは変更しない）。"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from config.config import OUTPUT_DIR, SITE_BUILD_ENABLED, SITE_IMPLEMENTATION_ENABLED

from modules.contract_workflow import ContractWorkBranch
from modules.site_build import _ensure_package_json, verify_site_build

logger = logging.getLogger(__name__)


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


class SiteImplementer:
    """ビルド検証のみ（成果物の自動パッチは行わない）。"""

    def __init__(self) -> None:
        pass

    def is_configured(self) -> bool:
        return True

    def implement(
        self,
        spec: dict,
        site_dir: Path,
        contract_plan: str = "",
        *,
        work_branch: ContractWorkBranch | None = None,
    ) -> tuple[bool, str]:
        """
        Returns:
            (成功, 最後のビルドログまたはメッセージ)
        """
        _ = contract_plan
        if work_branch is not None:
            logger.info(
                "サイト実装: 契約プラン作業分岐 work_branch=%s",
                work_branch.value,
            )
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

        if not SITE_BUILD_ENABLED:
            logger.info("SITE_BUILD_ENABLED=false のためビルド検証をスキップ")
            return True, "build_skipped"

        ok, blog = verify_site_build(site_dir, skip_install=False)
        if ok:
            logger.info("ビルド検証成功")
            return True, blog or ""
        return False, blog or ""
