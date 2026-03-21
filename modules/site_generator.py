"""サイト生成モジュール

仕様書のデザイン・構成に依存しない「技術要項の土台」のみをテンプレート化する。
ページ構成・セクション・見た目は LLM 実装または手動で追加する。
"""
import logging
import shutil
from pathlib import Path
from typing import Dict, List

from config.config import OUTPUT_DIR, TEMPLATE_DIR, get_common_technical_spec_prompt_block

logger = logging.getLogger(__name__)

NEXTJS_TEMPLATE_NAME = "nextjs_template"


class SiteGenerator:
    """Next.js 技術土台のみ生成（構成・デザインのテンプレートは含めない）"""

    def __init__(self):
        self.template_dir = TEMPLATE_DIR
        self.template_base = self.template_dir / NEXTJS_TEMPLATE_NAME
        self.output_dir = OUTPUT_DIR / "sites"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_site(
        self,
        spec: Dict,
        images: List[Dict[str, Path]],
        site_name: str,
    ) -> Path:
        """
        Next.js プロジェクトの技術土台を生成する。

        Args:
            spec: 仕様書（将来 LLM 実装で参照。土台生成ではデザイン・構成に使わない）
            images: 互換のため受け取るのみ（実ファイルは配置しない）
            site_name: ディレクトリ名

        Returns:
            生成されたサイトのパス
        """
        try:
            if not self.template_base.exists():
                raise FileNotFoundError(
                    f"テンプレートが見つかりません: {self.template_base}。"
                    "templates/nextjs_template/ を確認してください。"
                )

            site_dir = self.output_dir / site_name
            if site_dir.exists():
                shutil.rmtree(site_dir)

            shutil.copytree(self.template_base, site_dir, symlinks=False)

            self._apply_site_name(site_dir, site_name)
            self._write_tech_requirements(site_dir)
            self._skip_real_images(site_dir, images)

            logger.info("技術土台のみ生成しました: %s", site_dir)
            return site_dir

        except Exception as e:
            logger.error("サイト生成エラー: %s", e)
            raise

    def _apply_site_name(self, site_dir: Path, site_name: str) -> None:
        """package.json の name を site_name で置換"""
        pkg_path = site_dir / "package.json"
        text = pkg_path.read_text(encoding="utf-8")
        text = text.replace("{{SITE_NAME}}", site_name)
        pkg_path.write_text(text, encoding="utf-8")

    def _write_tech_requirements(self, site_dir: Path) -> None:
        """プラン共通の技術要項を動的生成"""
        tech_md = get_common_technical_spec_prompt_block()
        (site_dir / "TECH_REQUIREMENTS.md").write_text(tech_md, encoding="utf-8")

    def _skip_real_images(self, site_dir: Path, images: List[Dict[str, Path]]) -> None:
        """実画像は配置しない"""
        if images:
            logger.info(
                "画像ファイルは配置しません（%d 件）。ImagePlaceholder を使用してください。",
                len(images),
            )
