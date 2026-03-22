"""Next.js プロジェクトの npm ビルド検証"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_npm_install(site_dir: Path, timeout_sec: int = 600) -> tuple[bool, str]:
    """npm ci（推奨）または npm install を実行"""
    if not site_dir.is_dir():
        return False, f"サイトディレクトリが存在しません: {site_dir}"
    _ensure_package_json(site_dir)
    if not (site_dir / "package.json").is_file():
        return False, f"package.json が見つかりません: {site_dir / 'package.json'}"

    npm = shutil.which("npm")
    if not npm:
        return False, "npm が PATH にありません。Node.js をインストールしてください。"

    lock = site_dir / "package-lock.json"
    cmd = [npm, "ci"] if lock.exists() else [npm, "install"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(site_dir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env={**os.environ},
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        if proc.returncode != 0:
            return False, out
        return True, out
    except subprocess.TimeoutExpired:
        return False, "npm install/ci がタイムアウトしました"
    except Exception as e:
        return False, str(e)


def _ensure_package_json(site_dir: Path) -> None:
    """package.json の存在確認のみ（中身は Gemini 出力に委ねる。テンプレからの復元はしない）。"""
    if not site_dir.is_dir():
        logger.warning("site_dir が存在しないため package.json 確認をスキップ: %s", site_dir)
        return
    pkg = site_dir / "package.json"
    if not pkg.is_file():
        logger.warning(
            "package.json がありません。Gemini のフェンス出力に含めてください: %s", pkg
        )


def run_npm_build(site_dir: Path, timeout_sec: int = 900) -> tuple[bool, str]:
    """npm run build"""
    if not site_dir.is_dir():
        return False, f"サイトディレクトリが存在しません: {site_dir}"
    _ensure_package_json(site_dir)
    if not (site_dir / "package.json").is_file():
        return False, f"package.json が見つかりません: {site_dir / 'package.json'}"

    npm = shutil.which("npm")
    if not npm:
        return False, "npm が PATH にありません。"

    try:
        proc = subprocess.run(
            [npm, "run", "build"],
            cwd=str(site_dir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env={**os.environ},
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        if proc.returncode != 0:
            return False, out
        return True, out
    except subprocess.TimeoutExpired:
        return False, "npm run build がタイムアウトしました"
    except Exception as e:
        return False, str(e)


def run_npm_lint(site_dir: Path, timeout_sec: int = 300) -> tuple[bool, str]:
    """next lint（失敗してもビルド優先のため呼び出し側で任意）"""
    npm = shutil.which("npm")
    if not npm:
        return False, "npm が PATH にありません。"

    try:
        proc = subprocess.run(
            [npm, "run", "lint"],
            cwd=str(site_dir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        return proc.returncode == 0, out
    except Exception as e:
        return False, str(e)


def verify_site_build(site_dir: Path, skip_install: bool = False) -> tuple[bool, str]:
    """install → build を連続実行（skip_install=True で node_modules 既存時の再ビルドのみ）。

    ソースは変更しない（ビルド失敗時も自動パッチは行わない）。
    """
    _ensure_package_json(site_dir)
    if not skip_install:
        ok, log = run_npm_install(site_dir)
        if not ok:
            logger.error("npm install 失敗:\n%s", log[-8000:])
            return False, log

    ok, last_log = run_npm_build(site_dir)
    if ok:
        logger.info("npm run build が成功しました: %s", site_dir)
        return True, last_log

    logger.error("npm run build 失敗:\n%s", last_log[-8000:])
    return False, last_log
