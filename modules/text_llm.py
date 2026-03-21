"""
テキスト生成用 LLM（要望抽出・仕様書・サイト実装）。

- cursor_agent_cli: CURSOR_AGENT_COMMAND（例: bash scripts/cursor_agent_stdio.sh）
- claude_code_cli: CLAUDE_CODE_COMMAND

CLI は標準入力に SYSTEM / USER を渡し、標準出力を返答として読む。
"""
from __future__ import annotations

import logging
import os
import shlex
import subprocess
from typing import Optional

from config import config as cfg
from config.prompt_settings import get_text_llm_default_system

logger = logging.getLogger(__name__)

_CLI_PROVIDERS = frozenset({"cursor_agent_cli", "claude_code_cli"})


def resolve_text_llm_provider() -> str:
    """
    TEXT_LLM_PROVIDER が cursor_agent_cli | claude_code_cli。
    未設定時は CURSOR_AGENT_COMMAND があれば cursor、なければ claude、どちらもなければ cursor（未設定扱い）。
    """
    raw = (os.getenv("TEXT_LLM_PROVIDER") or "").strip().lower()
    if raw in _CLI_PROVIDERS:
        return raw
    if not raw:
        if (cfg.CURSOR_AGENT_COMMAND or "").strip():
            return "cursor_agent_cli"
        if (cfg.CLAUDE_CODE_COMMAND or "").strip():
            return "claude_code_cli"
        return "cursor_agent_cli"
    raise ValueError(
        f"TEXT_LLM_PROVIDER={raw!r} は未対応です。"
        "cursor_agent_cli または claude_code_cli を指定してください。"
    )


def is_text_llm_configured() -> bool:
    try:
        p = resolve_text_llm_provider()
    except ValueError:
        return False
    if p == "cursor_agent_cli":
        return bool((cfg.CURSOR_AGENT_COMMAND or "").strip())
    if p == "claude_code_cli":
        return bool((cfg.CLAUDE_CODE_COMMAND or "").strip())
    return False


def text_llm_complete(
    *,
    user: str,
    system: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 8192,
    model: Optional[str] = None,
    cli_timeout_sec: Optional[int] = None,
) -> str:
    """
    テキスト生成を1回実行する（CLI）。

    temperature / max_tokens / model は CLI では無視される（シグネチャ互換のため残す）。
    cli_timeout_sec: 未指定時は TEXT_LLM_CLI_TIMEOUT_SEC（既定 1200）。
    """
    _ = (temperature, max_tokens, model)
    provider = resolve_text_llm_provider()
    sys_prompt = system or get_text_llm_default_system()

    if provider == "claude_code_cli":
        cmd = (cfg.CLAUDE_CODE_COMMAND or "").strip()
        if not cmd:
            raise ValueError(
                "TEXT_LLM_PROVIDER=claude_code_cli ですが CLAUDE_CODE_COMMAND が空です"
            )
        return _complete_via_cli(cmd, sys_prompt, user, cli_timeout_sec=cli_timeout_sec)

    if provider == "cursor_agent_cli":
        cmd = (cfg.CURSOR_AGENT_COMMAND or "").strip()
        if not cmd:
            raise ValueError(
                "TEXT_LLM_PROVIDER=cursor_agent_cli ですが CURSOR_AGENT_COMMAND が空です"
            )
        return _complete_via_cli(cmd, sys_prompt, user, cli_timeout_sec=cli_timeout_sec)

    raise ValueError(f"未知の TEXT_LLM プロバイダ: {provider}")


def _complete_via_cli(
    command: str,
    system: str,
    user: str,
    *,
    cli_timeout_sec: Optional[int] = None,
) -> str:
    """CLI に全文を標準入力で渡し、標準出力を返す。"""
    full = f"=== SYSTEM ===\n{system}\n\n=== USER ===\n{user}"
    argv = shlex.split(command)
    timeout_sec = (
        int(cli_timeout_sec)
        if cli_timeout_sec is not None
        else int(os.getenv("TEXT_LLM_CLI_TIMEOUT_SEC", "1200"))
    )
    logger.info("TEXT_LLM CLI 実行: %s", argv[0] if argv else command)
    try:
        r = subprocess.run(
            argv,
            input=full,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            env={**os.environ},
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        logger.error("TEXT_LLM CLI タイムアウト: %s", e)
        raise
    if r.returncode != 0:
        raw_err = r.stderr or ""
        if isinstance(raw_err, bytes):
            raw_err = raw_err.decode("utf-8", errors="replace")
        err = str(raw_err).strip()[:4000]
        logger.error("TEXT_LLM CLI 失敗 exit=%s stderr=%s", r.returncode, err)
        hint = ""
        low = err.lower()
        if "usage limit" in low or "hit your usage" in low or "cursor pro" in low:
            hint = (
                " — Cursor CLI が利用上限を返しています（無料プランに落ちたとは限りません。"
                "Ultra でも agent -p は IDE と別枠で切れることがあります）。"
                "agent whoami でメール一致、agent logout && agent login、"
                "cursor.com の Usage/Billing 確認（SETUP.md の Cursor CLI 節）、"
                "または TEXT_LLM_PROVIDER=claude_code_cli + CLAUDE_CODE_COMMAND を検討してください。"
            )
        raise RuntimeError(
            f"TEXT_LLM CLI が失敗しました (exit {r.returncode}): {err}{hint}"
        )
    out = (r.stdout or "").strip()
    if not out:
        logger.warning("TEXT_LLM CLI の標準出力が空です")
    return out
