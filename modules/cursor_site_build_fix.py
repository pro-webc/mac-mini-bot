"""ビルド失敗時に Cursor CLI（agent）をサイトディレクトリで起動し、修正を試みる。"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

from config.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

_PROMPT_PATH = (
    PROJECT_ROOT / "config" / "prompts" / "cursor_site_build_fix" / "user_ja.txt"
)


def _resolve_agent_bin() -> str | None:
    if (p := os.getenv("CURSOR_AGENT_BIN", "").strip()) and Path(p).is_file():
        return p
    for name in ("agent",):
        w = shutil.which(name)
        if w:
            return w
    for p in (
        Path.home() / ".local/bin/agent",
        Path.home() / ".cursor/bin/agent",
    ):
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    return None


def cursor_site_build_fix_configured() -> bool:
    from config import config as cfg

    if not cfg.CURSOR_SITE_BUILD_FIX_ENABLED:
        return False
    script = Path(cfg.CURSOR_SITE_BUILD_FIX_SCRIPT)
    return script.is_file() and _resolve_agent_bin() is not None


def build_fix_prompt(*, site_dir: Path, build_log: str, tail_chars: int = 12000) -> str:
    site_dir = site_dir.resolve()
    tail = (build_log or "")[-tail_chars:] if build_log else "(ログなし)"
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(site_dir=str(site_dir), build_log_tail=tail)


def run_cursor_site_build_fix(
    site_dir: Path,
    build_log: str,
    *,
    timeout_sec: float,
) -> tuple[bool, str]:
    """
    Cursor CLI（scripts/cursor_agent_stdio.sh 経由）を site_dir を cwd にして実行。

    Returns:
        (プロセス成功, 結合 stdout/stderr)
    """
    from config import config as cfg

    site_dir = site_dir.resolve()
    script = Path(cfg.CURSOR_SITE_BUILD_FIX_SCRIPT)
    if not script.is_file():
        msg = f"CURSOR_SITE_BUILD_FIX_SCRIPT が見つかりません: {script}"
        logger.error(msg)
        return False, msg

    if not _resolve_agent_bin():
        msg = (
            "agent（Cursor CLI）が PATH にありません。"
            " https://cursor.com/docs/cli/overview の手順でインストールするか、"
            " CURSOR_AGENT_BIN を設定してください。"
        )
        logger.error(msg)
        return False, msg

    prompt = build_fix_prompt(site_dir=site_dir, build_log=build_log)
    shell = shutil.which("bash") or "/bin/bash"

    logger.info(
        "Cursor CLI によるビルド修復を開始します cwd=%s timeout=%ss",
        site_dir,
        timeout_sec,
    )
    try:
        proc = subprocess.run(
            [shell, str(script)],
            cwd=str(site_dir),
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=timeout_sec,
            env={**os.environ},
        )
    except subprocess.TimeoutExpired:
        msg = f"Cursor CLI 修復がタイムアウトしました（{timeout_sec}s）"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Cursor CLI 起動エラー: {e}"
        logger.error(msg, exc_info=True)
        return False, msg

    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    combined = (out + "\n" + err).strip()
    if proc.returncode != 0:
        logger.warning(
            "Cursor CLI 修復が非ゼロ終了 code=%s 出力末尾:\n%s",
            proc.returncode,
            combined[-4000:] if combined else "(空)",
        )
        return False, combined or f"exit {proc.returncode}"

    logger.info("Cursor CLI 修復コマンドは正常終了しました（出力長=%s）", len(combined))
    return True, combined
