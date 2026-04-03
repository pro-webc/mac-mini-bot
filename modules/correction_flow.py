"""修正フロー — AIワークフローシステム

制作済みサイトに対する Slack 修正指示を自動処理するパイプライン。

パイプライン:
  1. Slack から修正指示を取得
  2. output/<record>/llm_steps/ から生成トレースを読み、原因を調査
  3. 生成工程への改善提案を記録
  4. GitHub clone → Claude CLI で修正 → push
  5. 修正記録を output/<record>/correction_log/ に保存
  6. Slack に修正完了を報告
"""
from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import (
    CLAUDE_CLI_TIMEOUT_SEC,
    MANUS_API_BASE,
    MANUS_API_KEY,
    MANUS_AGENT_PROFILE,
    MANUS_INTERACTIVE_MODE,
    MANUS_REFACTOR_POLL_INTERVAL_SEC,
    MANUS_REFACTOR_TIMEOUT_SEC,
    MANUS_TASK_CONNECTOR_IDS,
    MANUS_TASK_MODE,
    OUTPUT_DIR,
    SLACK_BOT_TOKEN,
    SLACK_CORRECTION_CHANNEL_ID,
)
from modules.github_client import GitHubClient
from modules.llm.llm_step_trace import record_llm_turn
from modules.self_improvement import run_self_improvement
from modules.slack_client import (
    CorrectionMessage,
    SlackFetchError,
    fetch_correction_messages,
    post_message,
)
from modules.spreadsheet import SpreadsheetClient

logger = logging.getLogger(__name__)

# 生成工程の共通技術要件（修正フローにも適用する正本）
_TECH_SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "config" / "prompts" / "common" / "technical_spec_prompt_block.txt"
)


def _load_tech_spec() -> str:
    """technical_spec_prompt_block.txt を読み込む。存在しなければ空文字列。"""
    if _TECH_SPEC_PATH.is_file():
        return _TECH_SPEC_PATH.read_text(encoding="utf-8")
    logger.warning("技術要件ファイルが見つかりません: %s", _TECH_SPEC_PATH)
    return ""


# ---------------------------------------------------------------------------
# 1. Slack 修正指示の取得
# ---------------------------------------------------------------------------


def _fetch_slack_instructions(record_number: str) -> tuple[list[CorrectionMessage], str]:
    """Slack から修正指示を取得する。

    Returns:
        (messages, parent_thread_ts) — 親メッセージの ts（報告投稿用）。
        指示なしなら空リスト + 空文字列。
    """
    if not SLACK_BOT_TOKEN or not SLACK_CORRECTION_CHANNEL_ID:
        return [], ""

    try:
        msgs = fetch_correction_messages(
            token=SLACK_BOT_TOKEN,
            channel_id=SLACK_CORRECTION_CHANNEL_ID,
            record_number=record_number,
        )
    except SlackFetchError:
        logger.warning(
            "Slack 修正指示の取得に失敗しました record=%s", record_number,
            exc_info=True,
        )
        return [], ""

    if not msgs:
        return [], ""

    parent_ts = next((m.ts for m in msgs if not m.is_reply), msgs[0].ts)
    return msgs, parent_ts


def _format_slack_messages_for_prompt(msgs: list[CorrectionMessage]) -> str:
    """Slack メッセージを LLM プロンプト用テキストに整形する。"""
    lines: list[str] = []
    for m in msgs:
        prefix = "  └ リプライ" if m.is_reply else "投稿"
        lines.append(f"{prefix}: {m.text}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 1.5. 修正指示の構造化抽出
# ---------------------------------------------------------------------------


_EXTRACT_INSTRUCTIONS_PROMPT = """あなたはSlackスレッドから「サイト修正指示」だけを漏れなく抽出するアシスタントです。

## Slack スレッド全文
{raw_messages}

## タスク
上記スレッドには修正指示・業務連絡・雑談が混在しています。
以下のルールで **修正指示だけ** を構造化して抽出してください。

### 抽出ルール
- 「○○を変更」「○○を追加」「○○にしてほしい」等の **具体的なサイト変更依頼** を全て抽出する
- 親メッセージのテンプレート情報（参考サイトURL・指定色・問題の種類）も修正コンテキストとして含める
- 業務連絡・感想・叱責・承認・お礼は除外する
- 同じ指示が複数メッセージに分かれている場合は1つにまとめる
- 指示の意図が不明瞭でも、修正に関わりそうなら含める（除外より包含を優先）
- 画像添付への言及（「添付画像のような」等）は、画像自体は取得できないがテキスト指示として残す

### 出力フォーマット（JSON のみ出力）
```json
{{
  "context": {{
    "record_number": "レコード番号",
    "partner_name": "パートナー名",
    "site_url": "サイトURL",
    "specified_color": "指定色（あれば）",
    "reference_site": "参考サイトURL（あれば）",
    "site_type": "LP / CP 等",
    "design_category": "デザインカテゴリ（あれば）"
  }},
  "instructions": [
    {{
      "id": 1,
      "category": "color / layout / content / text / image / structure / map / other",
      "summary": "修正内容の端的な要約",
      "detail": "具体的な修正指示の全文（元のテキストをできるだけ忠実に）",
      "priority": "high / medium / low"
    }}
  ],
  "total_count": "抽出した修正指示の件数"
}}
```"""


def _extract_structured_instructions(
    raw_messages: str,
) -> dict[str, Any]:
    """Slack メッセージから修正指示だけを構造化抽出する。

    Returns:
        構造化された修正指示の辞書。抽出失敗時は空辞書。
    """
    prompt = _EXTRACT_INSTRUCTIONS_PROMPT.format(raw_messages=raw_messages)

    cli = shutil.which("claude")
    if not cli:
        logger.warning("claude CLI が見つかりません — 指示抽出をスキップ")
        return {}

    try:
        result = subprocess.run(
            [cli, "-p", prompt, "--output-format", "json", "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        record_llm_turn(kind="correction_extract_instructions", input_text=prompt, error_text="timeout")
        logger.warning("修正指示の抽出がタイムアウトしました")
        return {}

    stdout = result.stdout.strip()
    if not stdout:
        record_llm_turn(kind="correction_extract_instructions", input_text=prompt, error_text="empty output")
        return {}

    try:
        data = json.loads(stdout)
        text = data.get("result", "")
    except json.JSONDecodeError:
        text = stdout

    record_llm_turn(kind="correction_extract_instructions", input_text=prompt, output_text=text)

    import re
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


def _format_structured_instructions(extracted: dict[str, Any]) -> str:
    """構造化された修正指示をプロンプト用テキストに整形する。"""
    if not extracted:
        return ""

    lines: list[str] = []

    # コンテキスト情報
    ctx = extracted.get("context", {})
    if ctx:
        lines.append("## 案件コンテキスト")
        if ctx.get("specified_color"):
            lines.append(f"- 指定色: {ctx['specified_color']}")
        if ctx.get("reference_site"):
            lines.append(f"- 参考サイト: {ctx['reference_site']}")
        if ctx.get("design_category"):
            lines.append(f"- デザインカテゴリ: {ctx['design_category']}")
        if ctx.get("site_type"):
            lines.append(f"- サイトタイプ: {ctx['site_type']}")
        lines.append("")

    # 修正指示
    instructions = extracted.get("instructions", [])
    if instructions:
        lines.append(f"## 修正指示（{len(instructions)}件）")
        for inst in instructions:
            idx = inst.get("id", "?")
            cat = inst.get("category", "other")
            summary = inst.get("summary", "")
            detail = inst.get("detail", "")
            priority = inst.get("priority", "medium")
            lines.append(f"\n### [{idx}] {summary}（{cat} / {priority}）")
            lines.append(detail)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. 原因調査 — LLM トレースの読み取り
# ---------------------------------------------------------------------------


def _read_llm_trace_summary(record_number: str) -> str:
    """output/<record>/llm_steps/ からステップ一覧と各ステップの概要を返す。"""
    trace_dir = OUTPUT_DIR / str(record_number) / "llm_steps"
    if not trace_dir.is_dir():
        return "(LLM トレースなし)"

    lines: list[str] = []
    for step_dir in sorted(trace_dir.iterdir()):
        if not step_dir.is_dir():
            continue
        input_file = step_dir / "input.md"
        output_file = step_dir / "output.md"
        error_file = step_dir / "error.txt"

        status = "error" if error_file.exists() else "ok"
        input_preview = ""
        if input_file.exists():
            input_preview = input_file.read_text(errors="replace")[:200]
        output_preview = ""
        if output_file.exists():
            output_preview = output_file.read_text(errors="replace")[:200]

        lines.append(
            f"### {step_dir.name} [{status}]\n"
            f"入力冒頭: {input_preview}\n"
            f"出力冒頭: {output_preview}\n"
        )
    return "\n".join(lines) if lines else "(LLM トレースなし)"


# ---------------------------------------------------------------------------
# 3. Claude CLI による原因調査 + 修正実行
# ---------------------------------------------------------------------------


def _build_investigation_prompt(
    slack_text: str,
    trace_summary: str,
    partner_name: str,
    record_number: str,
) -> str:
    """原因調査プロンプトを組み立てる。"""
    return f"""あなたはWebサイト制作の品質改善エンジニアです。

## タスク
以下の修正指示の根本原因を調査し、JSON で回答してください。

## 案件情報
- レコード番号: {record_number}
- パートナー名: {partner_name}

## Slack 修正指示
{slack_text}

## 生成工程の LLM トレース（各ステップの入出力冒頭）
{trace_summary}

## 回答フォーマット（JSON のみ出力）
```json
{{
  "root_cause": {{
    "step": "問題の原因となった生成ステップ名（例: 004_claude_cli_chat）",
    "issue": "何が起きたかの端的な説明",
    "category": "問題カテゴリ（color_mismatch / content_missing / layout_issue / text_error / design_mismatch / other）"
  }},
  "improvement_suggestion": {{
    "target_file": "改善すべきプロンプトファイルのパス（例: config/prompts/basic_lp_manual/step_04_design_doc.txt）",
    "description": "具体的な改善提案"
  }}
}}
```"""


def _build_correction_prompt(
    slack_text: str,
    partner_name: str,
) -> str:
    """サイト修正実行用のプロンプトを組み立てる。"""
    tech_spec = _load_tech_spec()
    return f"""あなたはWebサイトの修正担当者です。
以下の修正指示に従い、このプロジェクトのファイルを直接編集してください。

## パートナー名
{partner_name}

## 修正指示（Slack より）
{slack_text}

## 修正時のルール
- 既存のデザイン・レイアウトを壊さない
- 修正量は最小限にする
- 新しい npm パッケージの追加は禁止
- API ルートの作成は禁止
- 画像の実ファイルは変更できないため、alt テキストや配置の修正のみ行う

## 生成工程の技術要件（修正でも必ず遵守すること）
以下はサイト生成パイプラインの共通技術要件です。修正時にもこの要件を全て守ってください。
特に絵文字禁止、shadow ルール、コピー正本の維持、日本語折り返しルールに注意。

{tech_spec}

修正が完了したら、変更したファイルの一覧と変更内容の要約を出力してください。"""


def _run_investigation(
    slack_text: str,
    trace_summary: str,
    partner_name: str,
    record_number: str,
) -> dict[str, Any]:
    """Claude CLI で原因調査を実行し、構造化された調査結果を返す。"""
    prompt = _build_investigation_prompt(
        slack_text, trace_summary, partner_name, record_number,
    )
    cli = shutil.which("claude")
    if not cli:
        logger.warning("claude CLI が見つかりません — 原因調査をスキップ")
        return {}

    try:
        result = subprocess.run(
            [cli, "-p", prompt, "--output-format", "json", "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        record_llm_turn(kind="correction_investigation", input_text=prompt, error_text="timeout")
        logger.warning("原因調査がタイムアウトしました")
        return {}

    stdout = result.stdout.strip()
    if not stdout:
        record_llm_turn(kind="correction_investigation", input_text=prompt, error_text="empty output")
        return {}

    try:
        data = json.loads(stdout)
        text = data.get("result", "")
    except json.JSONDecodeError:
        text = stdout

    record_llm_turn(kind="correction_investigation", input_text=prompt, output_text=text)

    # JSON ブロックを抽出
    import re
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    # フォールバック: テキスト全体を JSON として試行
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"raw_analysis": text[:1000]}


def _run_site_correction(
    site_dir: Path,
    slack_text: str,
    partner_name: str,
) -> str:
    """Claude CLI でサイトファイルを直接修正する。修正サマリを返す。"""
    prompt = _build_correction_prompt(slack_text, partner_name)
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("claude CLI が見つかりません")

    try:
        result = subprocess.run(
            [
                cli, "-p", prompt,
                "--output-format", "json",
                "--model", "claude-sonnet-4-6",
                "--allowedTools", "Edit,Write,Read,Glob,Grep",
            ],
            capture_output=True, text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            cwd=str(site_dir),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        record_llm_turn(kind="correction_site_fix", input_text=prompt, error_text="timeout")
        raise RuntimeError("修正の Claude CLI がタイムアウトしました") from e

    stdout = result.stdout.strip()
    if not stdout:
        record_llm_turn(kind="correction_site_fix", input_text=prompt, error_text=f"empty output. stderr: {result.stderr[:500]}")
        raise RuntimeError(f"Claude CLI の出力が空です。stderr: {result.stderr[:500]}")

    try:
        data = json.loads(stdout)
        output_text = data.get("result", stdout[:3000])
    except json.JSONDecodeError:
        output_text = stdout[:3000]

    record_llm_turn(kind="correction_site_fix", input_text=prompt, output_text=output_text)
    return output_text


# ---------------------------------------------------------------------------
# 3.5. 画像修正 — Manus に委譲
# ---------------------------------------------------------------------------


def _has_image_instructions(extracted: dict[str, Any]) -> list[dict[str, Any]]:
    """構造化抽出結果から画像カテゴリの指示を返す。"""
    if not extracted:
        return []
    return [
        inst for inst in extracted.get("instructions", [])
        if inst.get("category") in ("image",)
    ]


def _run_manus_image_correction(
    *,
    github_repo_url: str,
    image_instructions: list[dict[str, Any]],
    partner_name: str,
    record_number: str,
) -> str | None:
    """画像の差し替え・再生成が必要な指示を Manus に委譲する。

    Manus が GitHub リポジトリを直接操作し、nanobananaPro で画像を生成・配置する。

    Returns:
        Manus のレスポンス本文。Manus が利用不可または失敗時は None。
    """
    if not MANUS_API_KEY:
        logger.info("MANUS_API_KEY 未設定 — 画像修正をスキップ")
        return None

    import requests

    instructions_text = "\n".join(
        f"- [{inst.get('id', '?')}] {inst.get('summary', '')}: {inst.get('detail', '')}"
        for inst in image_instructions
    )

    prompt = f"""あなたはWebサイトの画像修正担当です。
以下の GitHub リポジトリのサイト画像を修正してください。

## リポジトリ
{github_repo_url}

## パートナー名
{partner_name}（レコード番号: {record_number}）

## 画像修正指示
{instructions_text}

## 作業手順
1. リポジトリを clone
2. 現在の public/images/ にある画像を確認
3. 修正指示に従い、nanobananaPro で新しい画像を生成
4. 生成した画像で既存画像を差し替え（ファイル名は変えない）
5. 必要に応じて新しい画像を追加
6. ImagePlaceholder コンポーネントが残っている場合は next/image の Image に置換
7. commit & push

## 画像生成ルール
- 日本人を指定（Japanese professional, Japanese woman 等）
- テキスト・ウォーターマークを画像に含めない
- アートメイクサロンの雰囲気に合った、清潔感のあるプロフェッショナルな画像
- 画像は public/images/ に配置し、src は /images/... のパスで参照

## 完了後
push した GitHub URL を以下の形式で出力:
BOT_DEPLOY_GITHUB_URL: {github_repo_url}
"""

    base = MANUS_API_BASE
    body: dict[str, Any] = {
        "prompt": prompt,
        "agentProfile": MANUS_AGENT_PROFILE,
        "interactiveMode": MANUS_INTERACTIVE_MODE,
    }
    if MANUS_TASK_MODE:
        body["taskMode"] = MANUS_TASK_MODE
    if MANUS_TASK_CONNECTOR_IDS:
        body["connectors"] = list(MANUS_TASK_CONNECTOR_IDS)

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "API_KEY": (MANUS_API_KEY or "").strip(),
    }

    logger.info("【画像修正】Manus タスク作成… record=%s 指示=%d件", record_number, len(image_instructions))

    try:
        r = requests.post(f"{base}/v1/tasks", headers=headers, json=body, timeout=120)
    except Exception:
        record_llm_turn(kind="correction_manus_image", input_text=prompt, error_text="task creation failed")
        logger.warning("Manus タスク作成に失敗しました", exc_info=True)
        return None

    if r.status_code != 200:
        record_llm_turn(kind="correction_manus_image", input_text=prompt, error_text=f"HTTP {r.status_code}: {r.text[:500]}")
        logger.warning("Manus タスク作成失敗 HTTP %d: %s", r.status_code, r.text[:300])
        return None

    created = r.json()
    task_id = str(created.get("task_id") or created.get("id") or "").strip()
    task_url = created.get("task_url")
    if task_url:
        logger.info("Manus 画像修正タスク URL: %s", task_url)

    # ポーリング
    from urllib.parse import urlparse
    poll_id = task_id
    if task_url:
        path = (urlparse(str(task_url)).path or "").rstrip("/")
        if path:
            slug = path.split("/")[-1]
            if slug:
                poll_id = slug

    timeout = float(MANUS_REFACTOR_TIMEOUT_SEC)
    interval = float(MANUS_REFACTOR_POLL_INTERVAL_SEC)
    deadline = time.time() + timeout

    while time.time() < deadline:
        time.sleep(interval)
        try:
            resp = requests.get(f"{base}/v1/tasks/{poll_id}", headers=headers, timeout=60)
        except Exception:
            logger.warning("Manus ポーリング失敗", exc_info=True)
            continue

        if resp.status_code == 404:
            # task_id にフォールバック
            if poll_id != task_id:
                poll_id = task_id
                continue
            continue

        if resp.status_code != 200:
            continue

        info = resp.json()
        status = (info.get("status") or "").lower()
        logger.info("Manus 画像修正 status=%s record=%s", status, record_number)

        if status in ("completed", "done", "finished"):
            output = info.get("output") or info.get("result") or ""
            output_text = str(output)[:3000] if output else "completed"
            record_llm_turn(kind="correction_manus_image", input_text=prompt, output_text=output_text)
            logger.info("Manus 画像修正完了 record=%s", record_number)
            return output_text

        if status in ("failed", "error", "cancelled"):
            record_llm_turn(kind="correction_manus_image", input_text=prompt, error_text=f"Manus status: {status}")
            logger.warning("Manus 画像修正が失敗しました status=%s", status)
            return None

    record_llm_turn(kind="correction_manus_image", input_text=prompt, error_text="timeout")
    logger.warning("Manus 画像修正がタイムアウトしました record=%s", record_number)
    return None


# ---------------------------------------------------------------------------
# 4. 修正記録の保存
# ---------------------------------------------------------------------------


def _save_correction_log(
    record_number: str,
    partner_name: str,
    slack_messages: list[CorrectionMessage],
    investigation: dict[str, Any],
    correction_summary: str,
    extracted_instructions: dict[str, Any] | None = None,
) -> Path:
    """修正記録を output/<record>/correction_log/ に保存する。"""
    log_dir = OUTPUT_DIR / str(record_number) / "correction_log"
    log_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"correction_{ts}.json"

    log_data = {
        "record_number": record_number,
        "partner_name": partner_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "slack_messages": [m.text for m in slack_messages],
        "extracted_instructions": extracted_instructions,
        "root_cause": investigation.get("root_cause", {}),
        "improvement_suggestion": investigation.get("improvement_suggestion", {}),
        "correction_summary": correction_summary,
    }

    log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("修正記録を保存: %s", log_path)
    return log_path


# ---------------------------------------------------------------------------
# 5. メインオーケストレーション
# ---------------------------------------------------------------------------


def process_correction(
    case: dict[str, Any],
    *,
    github_client: GitHubClient,
    spreadsheet: SpreadsheetClient,
) -> str | None:
    """修正フローの全工程を実行する。

    Returns:
        修正完了時は GitHub URL、スキップ時は None。
    """
    record_number = str(case.get("record_number") or "")
    partner_name = str(case.get("partner_name") or "")
    github_repo_url = str(case.get("github_repo_url") or "").strip()

    if not github_repo_url:
        logger.warning("github_repo_url が空のためスキップ record=%s", record_number)
        return None

    # --- Step 1: Slack 修正指示取得 ---
    logger.info("【修正フロー Step 1】Slack 修正指示を取得 record=%s", record_number)
    slack_msgs, parent_ts = _fetch_slack_instructions(record_number)
    if not slack_msgs:
        logger.info("Slack に修正指示なし — スキップ record=%s", record_number)
        return None

    raw_slack_text = _format_slack_messages_for_prompt(slack_msgs)
    logger.info("修正指示 %d 件取得（リプライ含む） record=%s", len(slack_msgs), record_number)

    # --- Step 1.5: 修正指示の構造化抽出 ---
    logger.info("【修正フロー Step 1.5】修正指示を構造化抽出 record=%s", record_number)
    extracted = _extract_structured_instructions(raw_slack_text)
    if extracted and extracted.get("instructions"):
        slack_text = _format_structured_instructions(extracted)
        logger.info(
            "修正指示を %s 件抽出 record=%s",
            extracted.get("total_count", len(extracted.get("instructions", []))),
            record_number,
        )
    else:
        logger.warning("構造化抽出に失敗 — 生メッセージをそのまま使用 record=%s", record_number)
        slack_text = raw_slack_text

    # --- Step 2: 原因調査 ---
    logger.info("【修正フロー Step 2】原因調査 record=%s", record_number)
    trace_summary = _read_llm_trace_summary(record_number)
    investigation = _run_investigation(
        slack_text, trace_summary, partner_name, record_number,
    )
    if investigation:
        root = investigation.get("root_cause", {})
        logger.info(
            "原因調査結果: step=%s category=%s issue=%s",
            root.get("step", "?"), root.get("category", "?"),
            root.get("issue", "?")[:100],
        )

    # --- Step 3: git clone ---
    logger.info("【修正フロー Step 3】GitHub clone record=%s", record_number)
    site_dir = OUTPUT_DIR / "sites" / f"{partner_name}-{record_number}"
    site_dir.mkdir(parents=True, exist_ok=True)
    github_client.shallow_clone_repo_into_site_dir(github_repo_url, site_dir)

    # --- Step 4: Claude CLI で修正（コード・テキスト・レイアウト系） ---
    logger.info("【修正フロー Step 4】Claude CLI で修正実行 record=%s", record_number)
    correction_summary = _run_site_correction(site_dir, slack_text, partner_name)
    logger.info("修正完了サマリ: %s", correction_summary[:200])

    # --- Step 4.5: 画像修正 — Manus に委譲 ---
    image_insts = _has_image_instructions(extracted)
    manus_image_result = None
    if image_insts:
        logger.info(
            "【修正フロー Step 4.5】画像修正を Manus に委譲 (%d件) record=%s",
            len(image_insts), record_number,
        )
        manus_image_result = _run_manus_image_correction(
            github_repo_url=github_repo_url,
            image_instructions=image_insts,
            partner_name=partner_name,
            record_number=record_number,
        )
        if manus_image_result:
            logger.info("Manus 画像修正完了 record=%s", record_number)
        else:
            logger.warning("Manus 画像修正なし/失敗 — コード修正のみ push record=%s", record_number)

    # --- Step 5: git push ---
    logger.info("【修正フロー Step 5】修正を push record=%s", record_number)
    github_client.add_commit_and_push(
        site_dir, github_repo_url,
        f"fix: Slack修正指示による自動修正 (record={record_number})",
    )

    # --- Step 6: 修正記録保存 ---
    logger.info("【修正フロー Step 6】修正記録を保存 record=%s", record_number)
    _save_correction_log(
        record_number, partner_name, slack_msgs,
        investigation, correction_summary,
        extracted_instructions=extracted,
    )

    # --- Step 7: 自己改善（プロンプトテンプレートの改善） ---
    logger.info("【修正フロー Step 7】自己改善 record=%s", record_number)
    improvement_result: dict[str, Any] = {}
    try:
        improvement_result = run_self_improvement(
            record_number=record_number,
            partner_name=partner_name,
            slack_text=slack_text,
            initial_investigation=investigation,
        )
        if improvement_result.get("success"):
            logger.info(
                "自己改善成功: target=%s description=%s",
                improvement_result.get("target_file", "?"),
                (improvement_result.get("description") or "")[:200],
            )
        else:
            logger.info("自己改善: 今回は適用なし record=%s", record_number)
    except Exception:
        logger.warning("自己改善でエラーが発生しましたが続行します", exc_info=True)

    # --- Step 8: Slack 報告 ---
    if SLACK_BOT_TOKEN and SLACK_CORRECTION_CHANNEL_ID and parent_ts:
        try:
            improvement_note = ""
            if improvement_result.get("success"):
                improvement_note = (
                    f"\n🔧 自己改善: {improvement_result.get('description', '')[:200]}"
                )
            report = (
                f"✅ 修正完了 — record={record_number} {partner_name}\n"
                f"変更内容: {correction_summary[:300]}"
                f"{improvement_note}"
            )
            post_message(
                token=SLACK_BOT_TOKEN,
                channel_id=SLACK_CORRECTION_CHANNEL_ID,
                text=report,
                thread_ts=parent_ts,
            )
        except SlackFetchError:
            logger.warning("Slack への修正報告投稿に失敗しました", exc_info=True)

    # --- スプレッドシート更新（レコード番号で行を再照合） ---
    try:
        fresh = spreadsheet.get_case_by_record_number(record_number)
        if fresh:
            spreadsheet.update_ai_status(fresh["row_number"], "デモサイト制作完了")
            logger.info(
                "ステータス更新: row=%s → 'デモサイト制作完了' record=%s",
                fresh["row_number"], record_number,
            )
        else:
            logger.warning(
                "レコード番号 %s がスプレッドシートに見つかりません — ステータス更新スキップ",
                record_number,
            )
    except Exception:
        logger.warning("修正完了ステータスの更新に失敗しました", exc_info=True)

    logger.info("✓ 修正フロー完了 record=%s", record_number)
    return github_repo_url
