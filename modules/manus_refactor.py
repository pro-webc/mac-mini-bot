"""最終リファクタ: Manus API（`POST /v1/tasks` → ポーリング）でフェンス付きマークダウンを取得する。

マニュアル本編は引き続き Gemini。リファクタのみ Manus。
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from config.config import (
    MANUS_AGENT_PROFILE,
    MANUS_API_BASE,
    MANUS_API_KEY,
    MANUS_REFACTOR_POLL_INTERVAL_SEC,
    MANUS_REFACTOR_TIMEOUT_SEC,
    MANUS_TASK_CONNECTOR_IDS,
    MANUS_TASK_MODE,
)

logger = logging.getLogger(__name__)

_BOT_DEPLOY_LINE_KEY = "bot_deploy_github_url"
_GITHUB_CLONE_URL_RE = re.compile(
    r"https://github\.com/[\w.-]+/[\w.-]+\.git",
    re.IGNORECASE,
)


def infer_manus_github_clone_url(
    text: str, *, record_number: str | None = None
) -> str | None:
    """
    Manus が作業ログのみ返し `BOT_DEPLOY_GITHUB_URL:` 行が無い／壊れているとき、
    本文中の ``https://github.com/owner/repo.git`` をレコード番号で絞って推定する。

    複数 URL で曖昧なときは None（誤デプロイ防止）。
    """
    raw = (text or "").strip()
    if not raw:
        return None
    found = _GITHUB_CLONE_URL_RE.findall(raw)
    if not found:
        return None

    def _norm(u: str) -> str:
        return u.rstrip(").,]}\"'")

    seen: set[str] = set()
    uniq: list[str] = []
    for u in found:
        n = _norm(u)
        if n not in seen:
            seen.add(n)
            uniq.append(n)

    rec = re.sub(r"\D", "", str(record_number or "").strip())
    if rec:
        hits = [u for u in uniq if rec in u]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return hits[-1]

    # 本番命名 bot-{record}-{name}。過去の demo-{record}-{name} も単一候補なら許容。
    bot_urls = [u for u in uniq if "bot-" in u.lower()]
    if len(bot_urls) == 1:
        return bot_urls[0]
    legacy_demo = [u for u in uniq if "demo-" in u.lower()]
    if len(legacy_demo) == 1:
        return legacy_demo[0]
    if len(uniq) == 1:
        return uniq[0]
    return None


def split_manus_response_deploy_url(response: str) -> tuple[str, str | None]:
    """
    Manus 返答から `BOT_DEPLOY_GITHUB_URL: https://github.com/...` を取り除き、(本文, URL) を返す。

    - **下から**見つかった `BOT_DEPLOY_GITHUB_URL:` 行を採用（その行より**後**の「タスク完了」等は本文に含めず捨てる）。
    - 行末が微妙に崩れているときは行単位の正規表現でもマッチ。
    """
    text = (response or "").rstrip()
    lines = text.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        raw = lines[i]
        s = raw.strip()
        if not s:
            continue
        parts = s.split(":", 1)
        if len(parts) == 2 and parts[0].strip().lower() == _BOT_DEPLOY_LINE_KEY:
            url = parts[1].strip().rstrip(").,]}\"'")
            body = "\n".join(lines[:i]).rstrip()
            return body, url or None
        m = re.match(r"^\s*BOT_DEPLOY_GITHUB_URL:\s*(\S+)", raw, re.IGNORECASE)
        if m:
            url = m.group(1).strip().rstrip(").,]}\"'")
            body = "\n".join(lines[:i]).rstrip()
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
    record_number: str | None = None,
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
        record_number=record_number,
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
    if MANUS_TASK_CONNECTOR_IDS:
        body["connectors"] = list(MANUS_TASK_CONNECTOR_IDS)

    logger.info(
        "%s Manus: 最終リファクタ タスク作成… agentProfile=%s taskMode=%s connectors=%s",
        _branch,
        MANUS_AGENT_PROFILE,
        MANUS_TASK_MODE or "(default)",
        len(MANUS_TASK_CONNECTOR_IDS) if MANUS_TASK_CONNECTOR_IDS else 0,
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
    task_id = (created or {}).get("task_id") or (created or {}).get("id")
    task_url = (created or {}).get("task_url")
    if not task_id and not task_url:
        raise RuntimeError(f"Manus 応答に task_id / task_url がありません: {created!r}")
    task_id = str(task_id or "").strip()
    task_url_slug: str | None = None
    if task_url:
        logger.info("Manus タスク URL: %s", task_url)
        path = (urlparse(str(task_url)).path or "").rstrip("/")
        if path:
            last = path.split("/")[-1]
            if last:
                task_url_slug = last

    # GET /v1/tasks/{id} は Create の task_id と manus.im URL のスラッグが一致しないと 404 になることがある。
    # スラッグを優先し、404 のときは task_id にフォールバックする。
    poll_candidates: list[str] = []
    if task_url_slug:
        poll_candidates.append(task_url_slug)
    if task_id and task_id not in poll_candidates:
        poll_candidates.append(task_id)
    if not poll_candidates:
        raise RuntimeError(f"Manus ポーリング用 ID を決められません: {created!r}")
    poll_idx = 0
    poll_id = poll_candidates[poll_idx]
    deadline = time.monotonic() + float(MANUS_REFACTOR_TIMEOUT_SEC)
    last_status = ""
    while time.monotonic() < deadline:
        url_get = f"{base}/v1/tasks/{poll_id}"
        gr = requests.get(url_get, headers=_headers(), timeout=60)
        if gr.status_code == 404 and poll_idx + 1 < len(poll_candidates):
            poll_idx += 1
            poll_id = poll_candidates[poll_idx]
            logger.warning(
                "Manus GetTask 404 のため別 ID でポーリングします → %s",
                poll_id,
            )
            time.sleep(min(2.0, float(MANUS_REFACTOR_POLL_INTERVAL_SEC)))
            continue
        if gr.status_code != 200:
            raise RuntimeError(
                f"Manus GetTask 失敗 HTTP {gr.status_code}: {(gr.text or '')[:800]}"
            )
        task = gr.json()
        status = (task or {}).get("status") or ""
        if status != last_status:
            logger.info("Manus タスク %s status=%s", poll_id, status)
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
                poll_id,
                len(text),
            )
            return text
        if status == "failed":
            err = (task or {}).get("error") or (task or {}).get("incomplete_details")
            raise RuntimeError(f"Manus タスク失敗: {err!r}")
        time.sleep(float(MANUS_REFACTOR_POLL_INTERVAL_SEC))

    raise RuntimeError(
        f"Manus タスクがタイムアウトしました（{MANUS_REFACTOR_TIMEOUT_SEC}s）: {poll_id}"
    )
