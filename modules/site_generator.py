"""サイト出力ディレクトリの準備

実装の正本は TEXT_LLM（Claude CLI）のフェンス出力のみ（`apply_contract_outputs_to_site_dir`）。
ここではコピー元テンプレは使わず、適用先フォルダと TECH_REQUIREMENTS.md のみ用意する。
"""
import logging
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, List

from config.config import OUTPUT_DIR, get_common_technical_spec_prompt_block

logger = logging.getLogger(__name__)


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


class SiteGenerator:
    """Claude CLI 出力の適用先ディレクトリのみ用意する（Next ファイルはコピーしない）。"""

    def __init__(self) -> None:
        self.output_dir = OUTPUT_DIR / "sites"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_site(
        self,
        spec: Dict,
        images: List[Dict[str, Path]],
        site_name: str,
    ) -> Path:
        """
        空のサイトディレクトリを用意し、技術要件メモのみ書く。

        package.json / app/ 等は ``apply_contract_outputs_to_site_dir`` が
        Claude CLI のマークダウンから書き込む。
        """
        try:
            site_dir = self.output_dir / site_name
            if site_dir.exists():
                _rmtree_existing_site(site_dir)

            site_dir.mkdir(parents=True, exist_ok=True)
            self._write_tech_requirements(site_dir)
            self._skip_real_images(site_dir, images)

            logger.info(
                "Claude CLI 出力の適用先を用意しました（テンプレコピーなし）: %s", site_dir
            )
            return site_dir

        except Exception as e:
            logger.error("サイト出力先の準備エラー: %s", e)
            raise

    def _write_tech_requirements(self, site_dir: Path) -> None:
        """プラン共通の技術要項を動的生成（参照用・push 対象）"""
        tech_md = get_common_technical_spec_prompt_block()
        (site_dir / "TECH_REQUIREMENTS.md").write_text(tech_md, encoding="utf-8")

    def _skip_real_images(self, site_dir: Path, images: List[Dict[str, Path]]) -> None:
        """実画像は配置しない"""
        if images:
            logger.info(
                "画像ファイルは配置しません（%d 件）。Claude CLI 出力で ImagePlaceholder を使ってください。",
                len(images),
            )
