"""最終リファクタ: Manus API（`POST /v1/tasks` → ポーリング）でフェンス付きマークダウンを取得する。

マニュアル本編は引き続き Gemini。リファクタのみ Manus。
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import requests
from config.config import (
    MANUS_AGENT_PROFILE,
    MANUS_API_BASE,
    MANUS_API_KEY,
    MANUS_REFACTOR_POLL_INTERVAL_SEC,
    MANUS_REFACTOR_TIMEOUT_SEC,
    MANUS_TASK_MODE,
)

logger = logging.getLogger(__name__)

BOT_DEPLOY_GITHUB_URL_PREFIX = "BOT_DEPLOY_GITHUB_URL:"


def split_manus_response_deploy_url(response: str) -> tuple[str, str | None]:
    """
    Manus 返答末尾の `BOT_DEPLOY_GITHUB_URL: https://github.com/...` を取り除き、(本文, URL) を返す。

    最後の非空行のみを URL 行として扱う。無ければ (response 全体, None)。
    """
    text = (response or "").rstrip()
    lines = text.split("\n")
    last_i = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            last_i = i
            break
    if last_i < 0:
        return text, None
    last = lines[last_i].strip()
    low = last.lower()
    pref_low = BOT_DEPLOY_GITHUB_URL_PREFIX.lower()
    if low.startswith(pref_low):
        url = last[len(BOT_DEPLOY_GITHUB_URL_PREFIX) :].strip()
        body = "\n".join(lines[:last_i]).rstrip()
        return body, url or None
    return text, None


def _headers() -> dict[str, str]:
    key = (MANUS_API_KEY or "").strip()
    if not key:
        raise RuntimeError(
            "MANUS_API_KEY が空です。最終リファクタは Manus API を使用します（.env に設定）。"
        )
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "API_KEY": key,
    }


def _extract_assistant_markdown(task: dict[str, Any]) -> str:
    """Get Task の ``output`` から assistant の output_text を連結。"""
    parts: list[str] = []
    for msg in task.get("output") or []:
        if (msg or {}).get("role") != "assistant":
            continue
        for block in (msg or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "output_text":
                continue
            t = block.get("text")
            if t:
                parts.append(str(t))
    return "\n\n".join(parts).strip()


def run_manus_refactor_stage(
    *,
    canvas_source_code: str,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
) -> str:
    """
    Manus にリファクタ用プロンプトを渡し、完了までポーリングして本文を返す。
    """
    # 遅延 import: basic_lp_refactor_gemini が本モジュールを import するため
    from modules import basic_lp_refactor_gemini as _ref

    prompt = _ref.build_basic_lp_refactor_user_prompt(
        canvas_source_code,
        preface_dir=preface_dir,
        partner_name=partner_name,
    )
    if preface_dir == _ref.ADVANCE_CP_REFACTOR_PREFACE_DIR:
        _branch = "ADVANCE-CP"
    elif preface_dir == _ref.STANDARD_CP_REFACTOR_PREFACE_DIR:
        _branch = "STANDARD-CP"
    elif preface_dir == _ref.BASIC_CP_REFACTOR_PREFACE_DIR:
        _branch = "BASIC-CP"
    else:
        _branch = "BASIC LP"

    base = MANUS_API_BASE
    url_create = f"{base}/v1/tasks"
    body: dict[str, Any] = {
        "prompt": prompt,
        "agentProfile": MANUS_AGENT_PROFILE,
    }
    if MANUS_TASK_MODE:
        body["taskMode"] = MANUS_TASK_MODE

    logger.info(
        "%s Manus: 最終リファクタ タスク作成… agentProfile=%s taskMode=%s",
        _branch,
        MANUS_AGENT_PROFILE,
        MANUS_TASK_MODE or "(default)",
    )
    r = requests.post(
        url_create,
        headers=_headers(),
        json=body,
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(
            f"Manus タスク作成失敗 HTTP {r.status_code}: {(r.text or '')[:800]}"
        )
    created = r.json()
    task_id = (created or {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"Manus 応答に task_id がありません: {created!r}")
    task_url = (created or {}).get("task_url")
    if task_url:
        logger.info("Manus タスク URL: %s", task_url)

    url_get = f"{base}/v1/tasks/{task_id}"
    deadline = time.monotonic() + float(MANUS_REFACTOR_TIMEOUT_SEC)
    last_status = ""
    while time.monotonic() < deadline:
        gr = requests.get(url_get, headers=_headers(), timeout=60)
        if gr.status_code != 200:
            raise RuntimeError(
                f"Manus GetTask 失敗 HTTP {gr.status_code}: {(gr.text or '')[:800]}"
            )
        task = gr.json()
        status = (task or {}).get("status") or ""
        if status != last_status:
            logger.info("Manus タスク %s status=%s", task_id, status)
            last_status = status
        if status == "completed":
            text = _extract_assistant_markdown(task)
            if not text.strip():
                raise RuntimeError(
                    "Manus タスクは completed ですが output_text が空です。"
                    f" metadata={task.get('metadata')!r}"
                )
            logger.info(
                "%s Manus: リファクタ完了 task_id=%s chars=%s",
                _branch,
                task_id,
                len(text),
            )
            return text
        if status == "failed":
            err = (task or {}).get("error") or (task or {}).get("incomplete_details")
            raise RuntimeError(f"Manus タスク失敗: {err!r}")
        time.sleep(float(MANUS_REFACTOR_POLL_INTERVAL_SEC))

    raise RuntimeError(
        f"Manus タスクがタイムアウトしました（{MANUS_REFACTOR_TIMEOUT_SEC}s）: {task_id}"
    )
