"""最終リファクタ: Manus API（`POST /v1/tasks` → ポーリング）でフェンス付きマークダウンを取得する。

マニュアル本編は引き続き Gemini。リファクタのみ Manus。
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import signal
import requests
from config.config import (
    MANUS_AGENT_PROFILE,
    MANUS_API_BASE,
    MANUS_API_KEY,
    MANUS_INTERACTIVE_MODE,
    MANUS_REFACTOR_POLL_INTERVAL_SEC,
    MANUS_REFACTOR_TIMEOUT_SEC,
    MANUS_TASK_CONNECTOR_IDS,
    MANUS_TASK_MODE,
)

logger = logging.getLogger(__name__)

# running→pending 遷移後、この秒数 pending が続いたらハングと判定して早期打ち切り
_PENDING_HANG_THRESHOLD = 600.0

_BOT_DEPLOY_LINE_KEY = "bot_deploy_github_url"
# 本文走査用（.git 省略・マークダウンリンク内の URL も search で拾う）
# [\w.%-]+ → パーセントエンコードされた日本語リポジトリ名にも対応
_GITHUB_CLONE_URL_RE = re.compile(
    r"https://github\.com/[\w.%-]+/[\w.%-]+(?:\.git)?",
    re.IGNORECASE,
)


def extract_github_clone_url_from_manus_fragment(fragment: str | None) -> str | None:
    """
    Manus が `BOT_DEPLOY_GITHUB_URL:` の値をプレーン以外で返したときの救済。

    - マークダウンリンク ``[表示名](https://github.com/...)``
    - 角括弧 ``<https://github.com/...>``
    - スプレッドシート等でハイパーリンク化された文字列に紛れた URL

    いずれも先頭の ``https://github.com/owner/repo(.git)?`` を抽出する。
    """
    if not fragment or not str(fragment).strip():
        return None
    s = str(fragment).strip()
    m = _GITHUB_CLONE_URL_RE.search(s)
    if not m:
        return None
    return m.group(0).rstrip(").,]}\"'")


def infer_manus_github_clone_url(
    text: str, *, record_number: str | None = None
) -> str | None:
    """
    Manus が作業ログのみ返し `BOT_DEPLOY_GITHUB_URL:` 行が無い／壊れているとき、
    本文中の ``https://github.com/owner/repo.git`` をレコード番号で絞って推定する。

    パーセントエンコードされた URL（日本語リポジトリ名）もデコードして判定する。
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
        # パーセントエンコードをデコードしてからレコード番号を照合
        hits = [u for u in uniq if rec in u or rec in unquote(u)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return hits[-1]

    # 本番命名 {record}-{ascii}。互換(旧): botrun-*、test-run-{record}、bot-{record}-*
    # デコードした URL でもプレフィックスを検索
    def _has_prefix(u: str) -> bool:
        low = u.lower()
        dec = unquote(u).lower()
        return any(
            p in low or p in dec
            for p in ("botrun-", "test-run-", "bot-")
        )

    pref_urls = [u for u in uniq if _has_prefix(u)]
    if len(pref_urls) == 1:
        return pref_urls[0]
    if len(pref_urls) > 1:
        return pref_urls[-1]
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
            raw_url = parts[1].strip().rstrip(").,]}\"'")
            url = extract_github_clone_url_from_manus_fragment(raw_url)
            body = "\n".join(lines[:i]).rstrip()
            return body, url
        m = re.match(r"^\s*BOT_DEPLOY_GITHUB_URL:\s*(.+)$", raw, re.IGNORECASE)
        if m:
            raw_url = m.group(1).strip().rstrip(").,]}\"'")
            url = extract_github_clone_url_from_manus_fragment(raw_url)
            body = "\n".join(lines[:i]).rstrip()
            return body, url
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
    """Get Task の ``output`` から assistant の output_text / text を連結。

    Manus API の output フォーマット:
      output: [ {role, content: [{type, text}, ...]}, ... ]
    content block の type は ``output_text`` が標準だが、
    API バージョンにより ``text`` 単独キーになる可能性もあるため両方を走査する。
    """
    parts: list[str] = []
    for msg in task.get("output") or []:
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "assistant":
            continue
        for block in msg.get("content") or []:
            if not isinstance(block, dict):
                continue
            btype = block.get("type") or ""
            if btype in ("output_text", "text"):
                t = block.get("text")
                if t:
                    parts.append(str(t))
    if not parts:
        # フォールバック: output 直下に text がある古い形式への対処
        for msg in task.get("output") or []:
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                t = msg.get("text")
                if t:
                    parts.append(str(t))
    return "\n\n".join(parts).strip()


def run_manus_refactor_stage(
    *,
    canvas_source_code: str,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
    record_number: str | None = None,
    hearing_reference_block: str | None = None,
    contract_max_pages: int | None = None,
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
        hearing_reference_block=hearing_reference_block,
        contract_max_pages=contract_max_pages,
    )
    from modules.llm.llm_step_trace import record_llm_turn

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
        "interactiveMode": MANUS_INTERACTIVE_MODE,
    }
    if MANUS_TASK_MODE:
        body["taskMode"] = MANUS_TASK_MODE
    if MANUS_TASK_CONNECTOR_IDS:
        body["connectors"] = list(MANUS_TASK_CONNECTOR_IDS)

    logger.warning(
        "%s Manus: 最終リファクタ タスク作成… agentProfile=%s taskMode=%s interactiveMode=%s connectors=%s",
        _branch,
        MANUS_AGENT_PROFILE,
        MANUS_TASK_MODE or "(default)",
        MANUS_INTERACTIVE_MODE,
        len(MANUS_TASK_CONNECTOR_IDS) if MANUS_TASK_CONNECTOR_IDS else 0,
    )
    try:
        r = requests.post(
            url_create,
            headers=_headers(),
            json=body,
            timeout=120,
        )
    except BaseException as e:
        record_llm_turn(
            kind="manus_refactor",
            input_text=prompt,
            error_text=f"{type(e).__name__}: {e}",
        )
        raise
    if r.status_code != 200:
        record_llm_turn(
            kind="manus_refactor",
            input_text=prompt,
            error_text=f"タスク作成 HTTP {r.status_code}: {(r.text or '')[:800]}",
        )
        raise RuntimeError(
            f"Manus タスク作成失敗 HTTP {r.status_code}: {(r.text or '')[:800]}"
        )
    try:
        created = r.json()
        task_id = (created or {}).get("task_id") or (created or {}).get("id")
        task_url = (created or {}).get("task_url")
        if not task_id and not task_url:
            raise RuntimeError(f"Manus 応答に task_id / task_url がありません: {created!r}")
        task_id = str(task_id or "").strip()
        task_url_slug: str | None = None
        if task_url:
            logger.warning("Manus タスク URL: %s", task_url)
            path = (urlparse(str(task_url)).path or "").rstrip("/")
            if path:
                last = path.split("/")[-1]
                if last:
                    task_url_slug = last

        # GET /v1/tasks/{id} は Create の task_id と manus.im URL のスラッグが一致しないと 404 になることがある。
        # スラッグを優先し、404 のときは task_id にフォールバックする。
        # 全候補が 404 でもタスク作成直後の伝播遅延を許容してリトライする。
        poll_candidates: list[str] = []
        if task_url_slug:
            poll_candidates.append(task_url_slug)
        if task_id and task_id not in poll_candidates:
            poll_candidates.append(task_id)
        if not poll_candidates:
            raise RuntimeError(f"Manus ポーリング用 ID を決められません: {created!r}")
        logger.warning(
            "Manus ポーリング開始 candidates=%s timeout=%ss",
            poll_candidates,
            MANUS_REFACTOR_TIMEOUT_SEC,
        )
        poll_idx = 0
        poll_id = poll_candidates[poll_idx]
        deadline = time.monotonic() + float(MANUS_REFACTOR_TIMEOUT_SEC)
        last_status = ""
        _max_404_rounds = 5
        _404_round = 0
        _404_backoff = 3.0

        _pending_since: float | None = None

        # SIGTERM/SIGINT でもトレースを残すためのハンドラ
        _interrupted = False
        _prev_sigterm = signal.getsignal(signal.SIGTERM)
        _prev_sigint = signal.getsignal(signal.SIGINT)

        def _on_signal(signum: int, _frame: Any) -> None:
            nonlocal _interrupted
            _interrupted = True

        signal.signal(signal.SIGTERM, _on_signal)
        signal.signal(signal.SIGINT, _on_signal)

        try:
            while time.monotonic() < deadline:
                if _interrupted:
                    raise RuntimeError(
                        f"Manus ポーリング中にシグナルを受信しました"
                        f" task={poll_id} last_status={last_status!r}"
                    )
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
                if gr.status_code == 404:
                    _404_round += 1
                    if _404_round >= _max_404_rounds:
                        raise RuntimeError(
                            f"Manus GetTask 失敗 HTTP 404（{_404_round} 回リトライ後）: {(gr.text or '')[:800]}"
                        )
                    wait = min(_404_backoff * _404_round, 15.0)
                    logger.warning(
                        "Manus GetTask 404 — 伝播待ちリトライ %d/%d（%.0fs 後に再試行）",
                        _404_round,
                        _max_404_rounds,
                        wait,
                    )
                    poll_idx = 0
                    poll_id = poll_candidates[poll_idx]
                    time.sleep(wait)
                    continue
                if gr.status_code != 200:
                    raise RuntimeError(
                        f"Manus GetTask 失敗 HTTP {gr.status_code}: {(gr.text or '')[:800]}"
                    )
                task = gr.json()
                status = (task or {}).get("status") or ""
                if status != last_status:
                    logger.warning("Manus タスク %s status=%s", poll_id, status)
                    last_status = status
                if status == "completed":
                    text = _extract_assistant_markdown(task)
                    if not text.strip():
                        raise RuntimeError(
                            "Manus タスクは completed ですが output_text が空です。"
                            f" metadata={task.get('metadata')!r}"
                        )
                    record_llm_turn(
                        kind="manus_refactor",
                        input_text=prompt,
                        output_text=text,
                    )
                    logger.warning(
                        "%s Manus: リファクタ完了 task_id=%s chars=%s",
                        _branch,
                        poll_id,
                        len(text),
                    )
                    return text
                if status == "failed":
                    err = (task or {}).get("error") or (task or {}).get("incomplete_details")
                    raise RuntimeError(f"Manus タスク失敗: {err!r}")

                # running→pending 遷移の検出: interactiveMode=false なのに pending が続く場合はハング
                if status == "pending":
                    if _pending_since is None:
                        _pending_since = time.monotonic()
                    elif (
                        not MANUS_INTERACTIVE_MODE
                        and time.monotonic() - _pending_since > _PENDING_HANG_THRESHOLD
                    ):
                        elapsed_pending = time.monotonic() - _pending_since
                        raise RuntimeError(
                            f"Manus タスクが pending のまま {elapsed_pending:.0f}s 経過しました"
                            f"（interactiveMode=false なのにユーザー入力待ちの可能性）。"
                            f" task={poll_id}"
                        )
                else:
                    _pending_since = None

                time.sleep(float(MANUS_REFACTOR_POLL_INTERVAL_SEC))

            raise RuntimeError(
                f"Manus タスクがタイムアウトしました（{MANUS_REFACTOR_TIMEOUT_SEC}s）"
                f" task={poll_id} last_status={last_status!r}"
            )
        finally:
            signal.signal(signal.SIGTERM, _prev_sigterm)
            signal.signal(signal.SIGINT, _prev_sigint)
    except BaseException as e:
        record_llm_turn(
            kind="manus_refactor",
            input_text=prompt,
            error_text=f"{type(e).__name__}: {e}",
        )
        raise
