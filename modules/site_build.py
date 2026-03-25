"""Next.js プロジェクトの npm ビルド検証"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

from config.config import SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT

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


# コンテンツページではないシステム系ルート（契約ページ数のカウント対象外）。
# app/ 直下のディレクトリ名で判定する。
_NON_CONTENT_ROUTE_PREFIXES: frozenset[str] = frozenset({
    "api",
    "preview",
    "_next",
})


def _is_non_content_route(rel_path: str) -> bool:
    """app/preview/[id]/page.tsx のようなシステム系ルートなら True。"""
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        route_dir = parts[1]  # app/{route_dir}/...
        if route_dir in _NON_CONTENT_ROUTE_PREFIXES or route_dir.startswith("_"):
            return True
    return False


def count_app_router_page_tsx_files(
    site_dir: Path,
) -> tuple[int, list[str]]:
    """App Router の `page.tsx` 本数と相対パス一覧（契約ページ数との突合せ用）。

    `app/` と `src/app/` の両方を走査する。
    node_modules と、コンテンツページでないシステム系ルート（api, preview 等）は除外。
    """
    paths: list[str] = []
    excluded: list[str] = []
    site_dir = site_dir.resolve()
    for base in ("app", "src/app"):
        root = site_dir / base
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("page.tsx")):
            if "node_modules" in p.parts:
                continue
            try:
                rel = p.relative_to(site_dir)
            except ValueError:
                rel = p
            rel_str = str(rel).replace("\\", "/")
            if _is_non_content_route(rel_str):
                excluded.append(rel_str)
                continue
            paths.append(rel_str)
    if excluded:
        logger.info(
            "page.tsx カウント対象外（システムルート）: %s", ", ".join(excluded)
        )
    return len(paths), paths


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


def verify_site_build(
    site_dir: Path,
    skip_install: bool = False,
    *,
    contract_max_pages: int | None = None,
) -> tuple[bool, str]:
    """install → build を連続実行（skip_install=True で node_modules 既存時の再ビルドのみ）。

    ソースは変更しない（ビルド失敗時も自動パッチは行わない）。

    contract_max_pages:
        指定かつ ``SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT`` が真のとき、
        App Router の ``page.tsx`` 本数がこれを超えたらビルド前に失敗する。
    """
    _ensure_package_json(site_dir)
    if (
        SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT
        and contract_max_pages is not None
        and int(contract_max_pages) >= 1
    ):
        n, rels = count_app_router_page_tsx_files(site_dir)
        cap = int(contract_max_pages)
        if n > cap:
            msg = (
                f"契約ページ数（{cap}）を超える App Router の page.tsx が {n} 本あります。"
                f" 余分なルート（例: /privacy）を増やさないでください。"
                f" 検出: {', '.join(rels)}"
            )
            logger.error(msg)
            return False, msg
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
