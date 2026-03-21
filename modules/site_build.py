"""Next.js プロジェクトの npm ビルド検証"""
from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

from config.config import TEMPLATE_DIR

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
    """package.json 欠落時はテンプレートから最小復元する。"""
    if not site_dir.is_dir():
        logger.warning("site_dir が存在しないため package.json 復元をスキップ: %s", site_dir)
        return
    pkg = site_dir / "package.json"
    if pkg.is_file():
        return
    template_pkg = TEMPLATE_DIR / "nextjs_template" / "package.json"
    if not template_pkg.is_file():
        return
    text = template_pkg.read_text(encoding="utf-8").replace("{{SITE_NAME}}", site_dir.name)
    pkg.write_text(text, encoding="utf-8")
    logger.warning("package.json が欠落していたためテンプレートから復元: %s", pkg)


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


_WEBPACK_UNRESOLVED_RE = re.compile(r"Can't resolve ['\"](@/[^'\"]+)['\"]")


def _stub_tsx_for_component(component_name: str) -> str:
    """不足モジュール用の最小 TSX（ビルド通過用。LLM 実装で上書き前提）"""
    if "Footer" in component_name:
        return f"""export default function {component_name}() {{
  return (
    <footer className="border-t border-neutral-200 p-4">
      <p className="text-sm text-neutral-500">{component_name}（stub）</p>
    </footer>
  );
}}
"""
    if "Header" in component_name:
        return f"""export default function {component_name}() {{
  return (
    <header className="border-b border-neutral-200 p-4">
      <p className="text-sm text-neutral-500">{component_name}（stub）</p>
    </header>
  );
}}
"""
    return f"""export default function {component_name}() {{
  return (
    <section className="py-8 px-4 border border-dashed border-neutral-300 rounded-lg">
      <p className="text-sm text-neutral-500">{component_name}（stub）</p>
    </section>
  );
}}
"""


def apply_webpack_missing_module_stubs(site_dir: Path, build_log: str) -> int:
    """
    `Module not found: Can't resolve '@/...'` に対し、不足ファイルのプレースホルダー TSX を生成する。
    既存ファイルは上書きしない。
    Returns:
        新規作成したファイル数
    """
    site_dir = site_dir.resolve()
    aliases = sorted(set(_WEBPACK_UNRESOLVED_RE.findall(build_log)))
    n = 0
    for alias in aliases:
        if not alias.startswith("@/"):
            continue
        rel = alias[2:].lstrip("/")
        if not rel or ".." in rel:
            continue
        target = site_dir / rel
        if target.suffix not in (".tsx", ".ts", ".jsx", ".js"):
            target = target.with_suffix(".tsx")
        if target.exists():
            continue
        try:
            target.relative_to(site_dir)
        except ValueError:
            continue
        comp_name = target.stem
        if not comp_name.isidentifier():
            comp_name = "StubComponent"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_stub_tsx_for_component(comp_name), encoding="utf-8")
        logger.warning(
            "不足モジュールを stub 作成: %s",
            target.relative_to(site_dir),
        )
        n += 1
    return n


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
    """install → build を連続実行（skip_install=True で node_modules 既存時の再ビルドのみ）"""
    _ensure_package_json(site_dir)
    if not skip_install:
        ok, log = run_npm_install(site_dir)
        if not ok:
            logger.error("npm install 失敗:\n%s", log[-8000:])
            return False, log

    last_log = ""
    # LLM が import だけ先に書いてコンポーネントを出し忘れた場合、stub を足して再ビルド
    for _round in range(12):
        ok, last_log = run_npm_build(site_dir)
        if ok:
            logger.info("npm run build が成功しました: %s", site_dir)
            return True, last_log
        n_stub = apply_webpack_missing_module_stubs(site_dir, last_log)
        if n_stub == 0:
            break
        logger.info(
            "不足モジュール stub を %s 件追加したため npm run build を再試行します（%s/12）",
            n_stub,
            _round + 1,
        )

    logger.error("npm run build 失敗:\n%s", last_log[-8000:])
    return False, last_log


def verify_site_build_with_cursor_pass(
    site_dir: Path,
    *,
    skip_install_first: bool = False,
) -> tuple[bool, str]:
    """
    通常の install→build（stub 再試行込み）のあと、有効なら必ず Cursor CLI でチェック・修正し、再ビルドする。
    無効時は従来どおり 1 回の verify_site_build のみ。
    """
    from config import config as cfg
    from modules.cursor_site_build_fix import (
        cursor_site_build_fix_configured,
        run_cursor_site_build_fix,
    )

    ok, log = verify_site_build(site_dir, skip_install=skip_install_first)
    if not cfg.CURSOR_SITE_BUILD_FIX_ENABLED:
        return ok, log
    if not cursor_site_build_fix_configured():
        logger.warning(
            "CURSOR_SITE_BUILD_FIX_ENABLED ですが agent またはスクリプトが無いため Cursor パスをスキップします"
        )
        return ok, log

    logger.info("Cursor チェック・修正フェーズ（CLI）を実行します…")
    inv_ok, fix_out = run_cursor_site_build_fix(
        site_dir,
        log,
        timeout_sec=cfg.CURSOR_SITE_BUILD_FIX_TIMEOUT_SEC,
    )
    if fix_out:
        logger.debug("Cursor 出力末尾:\n%s", fix_out[-2500:])
    if not inv_ok:
        logger.warning("Cursor CLI が非ゼロ終了しました。続けて npm run build のみ再試行します。")

    ok2, log2 = verify_site_build(site_dir, skip_install=True)
    return ok2, log2
