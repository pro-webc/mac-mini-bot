"""サイト生成モジュール

仕様書のデザイン・構成に依存しない「技術要項の土台」のみをテンプレート化する。
ページ構成・セクション・見た目は LLM 実装または手動で追加する。
"""
import logging
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, List

from config.config import (
    OUTPUT_DIR,
    SITE_KEEP_TEMPLATE_APP_ROUTES,
    TEMPLATE_DIR,
    get_common_technical_spec_prompt_block,
)

logger = logging.getLogger(__name__)

NEXTJS_TEMPLATE_NAME = "nextjs_template"


def _delete_tree_aggressive(path: Path) -> None:
    """ディレクトリを消す（ignore_errors + rm -rf）。"""
    if not path.exists():
        return
    try:
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass
    try:
        subprocess.run(
            ["rm", "-rf", str(path)],
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.error("rm -rf 失敗: %s — %s", path, e)


def _rmtree_existing_site(site_dir: Path) -> None:
    """
    既存 output サイトを削除。

    next dev 等が .next / node_modules を掴むと rmtree が [Errno 66] Directory not empty
    等で失敗することがあるため、**同一ボリューム上で rename 退避**してから元パスを空け、
    退避先は rm -rf で掃除する。
    """
    if not site_dir.is_dir():
        return

    parent = site_dir.parent
    name = site_dir.name
    backup = parent / f".trash-{name}-{os.getpid()}-{uuid.uuid4().hex[:10]}"
    while backup.exists():
        backup = parent / f".trash-{name}-{os.getpid()}-{uuid.uuid4().hex[:10]}"

    try:
        site_dir.rename(backup)
        logger.info("既存サイトを退避しました（削除処理へ）: %s", backup)
        _delete_tree_aggressive(backup)
        if backup.exists():
            logger.warning("退避フォルダの削除が不完全です（手動で削除可）: %s", backup)
        return
    except OSError as e:
        logger.warning(
            "既存サイトの rename 退避に失敗（従来の削除へ）: %s — %s",
            site_dir,
            e,
        )

    for attempt in range(2):
        try:
            shutil.rmtree(site_dir)
            return
        except OSError as err:
            logger.warning(
                "既存サイト削除を再試行します (%s/2): %s — %s",
                attempt + 1,
                site_dir,
                err,
            )
            time.sleep(0.6)
    _delete_tree_aggressive(site_dir)
    if site_dir.exists():
        raise OSError(
            f"既存サイトを削除できませんでした（next dev を止めて再実行してください）: {site_dir}"
        )

# app 直下に残すファイル（ルートレイアウト・トップページのみ。他は実装 LLM が仕様の page_structure で追加）
_APP_ROOT_KEEP_FILES = frozenset(
    {
        "layout.tsx",
        "page.tsx",
        "globals.css",
        "favicon.ico",
        "loading.tsx",
        "error.tsx",
        "not-found.tsx",
        "template.tsx",
        "default.tsx",
    }
)


def _prune_template_app_subroutes(site_dir: Path) -> None:
    """
    テンプレに同梱の app/about, app/blog 等を削除する。
    残すと STANDARD=6 でも実 URL が十数本になり契約と不一致になるため。
    """
    app = site_dir / "app"
    if not app.is_dir():
        return
    removed_dirs: list[str] = []
    for child in list(app.iterdir()):
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
            removed_dirs.append(child.name)
    for child in list(app.iterdir()):
        if not child.is_file():
            continue
        if child.name in _APP_ROOT_KEEP_FILES:
            continue
        if child.suffix.lower() in (".tsx", ".ts", ".jsx", ".js", ".css"):
            try:
                child.unlink()
            except OSError:
                pass
    if removed_dirs:
        logger.info(
            "テンプレの app サブルートを削除しました（契約ページ数は実装 LLM が追加）: %s",
            ", ".join(sorted(removed_dirs)),
        )


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
                _rmtree_existing_site(site_dir)

            shutil.copytree(self.template_base, site_dir, symlinks=False)

            if not SITE_KEEP_TEMPLATE_APP_ROUTES:
                _prune_template_app_subroutes(site_dir)

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
