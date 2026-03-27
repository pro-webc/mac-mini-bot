"""4 つの ``*_claude_manual.py`` で共通のヘルパー関数・定数。

テキスト LLM は Claude Code CLI（``claude -p``）を使用する。
各パイプラインファイルはプラン固有のステップ定義のみを保持し、
共通インフラはここから import する。
"""
from __future__ import annotations

import json
import logging
import shutil
import subprocess
import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.contract_workflow import ContractWorkBranch

import re as _re

from config.config import CLAUDE_CLI_TIMEOUT_SEC
from modules.hearing_url_utils import existing_site_url_guess_from_hearing

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Claude Code CLI 実行基盤
# ---------------------------------------------------------------------------


def _run_claude_cli(
    prompt: str,
    *,
    model: str,
    session_id: str | None = None,
    resume: bool = False,
    module_name: str = "",
) -> dict[str, Any]:
    """claude -p でプロンプトを実行し、JSON レスポンスを返す。

    引数: prompt — 送信テキスト / model — CLI の --model / session_id・resume — マルチターン用
    処理: subprocess.run → claude CLI → JSON parse。exit code != 0 かつ result 空で RuntimeError
    出力: CLI の JSON レスポンス辞書（type, result, usage 等）
    """
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("claude CLI が見つかりません。npm install -g @anthropic-ai/claude-code を実行してください。")

    cmd: list[str] = [
        cli, "-p", prompt,
        "--tools", "",
        "--output-format", "json",
        "--model", model,
    ]
    if resume and session_id:
        cmd.extend(["--resume", session_id])
    elif session_id:
        cmd.extend(["--session-id", session_id])
    else:
        cmd.append("--no-session-persistence")

    prefix = f"{module_name}: " if module_name else ""
    logger.debug("%sClaude CLI 実行: model=%s resume=%s", prefix, model, resume)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"{prefix}Claude CLI がタイムアウトしました（{CLAUDE_CLI_TIMEOUT_SEC}秒）。"
        ) from e

    stdout = result.stdout.strip()
    if not stdout:
        raise RuntimeError(
            f"{prefix}Claude CLI の出力が空です。stderr: {result.stderr[:500]}"
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"{prefix}Claude CLI の JSON パースに失敗: {e}\nstdout: {stdout[:500]}"
        ) from e

    if data.get("is_error"):
        raise RuntimeError(
            f"{prefix}Claude CLI エラー: {data.get('result', '(不明)')}"
        )

    return data


def _extract_cli_text(
    data: dict[str, Any],
    *,
    module_name: str = "",
) -> str:
    """CLI JSON レスポンスから応答テキストを抽出。空なら例外。"""
    text = (data.get("result") or "").strip()
    if not text:
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(f"{prefix}Claude CLI 応答テキストが空です。")
    return text


# ---------------------------------------------------------------------------
# 単発テキスト生成 / マルチターンチャット
# ---------------------------------------------------------------------------


def generate_text(
    prompt: str,
    *,
    model: str,
    module_name: str = "",
) -> str:
    """単発テキスト生成。

    引数: prompt — ユーザープロンプト / model — CLI --model 値
    処理: _run_claude_cli を単発（セッションなし）で呼び出し
    出力: 応答テキスト（str）
    """
    from modules.llm.llm_step_trace import record_llm_turn

    data = _run_claude_cli(prompt, model=model, module_name=module_name)
    text = _extract_cli_text(data, module_name=module_name)
    record_llm_turn(kind="claude_cli_generate", input_text=prompt, output_text=text)
    return text


class ClaudeCLIChat:
    """Claude Code CLI でのマルチターンチャットを管理する。

    session_id を内部で保持し、初回は --session-id UUID で開始、
    2 回目以降は --resume UUID で継続する。

    history を渡すと、初回メッセージに会話履歴をコンテキストとして埋め込む
    （段階テストで途中からチャットを再開する用途）。
    """

    def __init__(
        self,
        *,
        model: str,
        module_name: str = "",
        history: list[dict[str, str]] | None = None,
    ) -> None:
        self._model = model
        self._module_name = module_name
        self._session_id = str(uuid.uuid4())
        self._turn_count = 0
        self._pending_history = history

    def send_message(self, content: str) -> str:
        """メッセージを送信し、応答テキストを返す。

        引数: content — ユーザーメッセージ
        処理: 初回は新規セッション作成（history があればコンテキスト埋め込み）、
              2 回目以降はセッション継続
        出力: 応答テキスト（str）
        """
        from modules.llm.llm_step_trace import record_llm_turn

        actual_content = content
        if self._turn_count == 0 and self._pending_history:
            lines = ["【これまでの会話履歴（コンテキスト）】"]
            for msg in self._pending_history:
                role_label = "ユーザー" if msg["role"] == "user" else "アシスタント"
                lines.append(f"\n--- {role_label} ---\n{msg['content']}")
            lines.append(f"\n【新しいメッセージ（これに回答してください）】\n{content}")
            actual_content = "\n".join(lines)

        resume = self._turn_count > 0
        data = _run_claude_cli(
            actual_content,
            model=self._model,
            session_id=self._session_id,
            resume=resume,
            module_name=self._module_name,
        )
        text = _extract_cli_text(data, module_name=self._module_name)
        self._turn_count += 1
        record_llm_turn(
            kind="claude_cli_chat",
            input_text=content,
            output_text=text,
        )
        return text


# ---------------------------------------------------------------------------
# プロンプト読み込み・置換ヘルパー（LLM 非依存）
# ---------------------------------------------------------------------------


def load_step(manual_dir: Path, filename: str, *, module_name: str = "") -> str:
    """プロンプトファイルをロード。存在しなければ RuntimeError。"""
    path = manual_dir / filename
    if not path.is_file():
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(f"{prefix}マニュアルプロンプトが見つかりません: {path}")
    return path.read_text(encoding="utf-8")


def subst(template: str, *, module_name: str = "", **kwargs: str) -> str:
    """``{{KEY}}`` プレースホルダを置換し、未置換が残れば例外。"""
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", value)
    if "{{" in out and "}}" in out:
        i = out.index("{{")
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(
            f"{prefix}プレースホルダが未置換です: " + out[i : i + 80]
        )
    return out


def hearing_block(hearing_sheet_content: str, *, module_name: str = "") -> str:
    """ヒアリング本文を検証して返す。空なら例外。"""
    h = (hearing_sheet_content or "").strip()
    if not h:
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(f"{prefix}ヒアリングシート本文が空です。")
    return h


def existing_site_url_block(hearing_sheet_content: str, explicit: str) -> str:
    u = (explicit or "").strip()
    if not u:
        u = existing_site_url_guess_from_hearing(hearing_sheet_content)
    if u:
        return u
    return "（既存サイトURLの記載なし。ヒアリング本文に URL があればそちらを参照）"


def client_hp_and_mood_placeholders() -> tuple[str, str]:
    """手順5の「〇〇」相当。人間作業では手入力するため、自動実行時はモデルへの指示文とする。"""
    return (
        "（ヒアリングシート設問「ホームページに使いたい色」および手順1-3の記載を最優先。未記載なら本文から判断）",
        "（ヒアリングシート設問「希望の雰囲気」および手順1-3の記載を最優先。未記載なら本文から判断）",
    )


def reference_url_block(
    hearing_sheet_content: str,
    *,
    extra_texts: Sequence[str] = (),
) -> str:
    """後方互換用。LLM 抽出版 ``reference_url_block_from_extracted`` を使うこと。"""
    return "（参考サイトURLの記載なし。手順1-3およびヒアリング本文を参照）"


# ---------------------------------------------------------------------------
# LLM による参考サイト URL 抽出（Python 正規表現に代わる新工程）
# ---------------------------------------------------------------------------

_COMMON_PROMPT_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "common"
_URL_EXTRACT_PROMPT_FILE = "extract_reference_urls.txt"


def _load_url_extract_template(*, module_name: str = "") -> str:
    return load_step(_COMMON_PROMPT_DIR, _URL_EXTRACT_PROMPT_FILE, module_name=module_name)


def _parse_url_extraction_response(text: str) -> list[dict[str, str]]:
    """LLM 応答から JSON 配列を抽出しパース。失敗時は空リスト。"""
    m = _re.search(r"\[.*\]", text, _re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [
        {
            "url": str(item.get("url", "")).strip(),
            "design_intent": str(item.get("design_intent", "参考サイト")).strip(),
        }
        for item in data
        if isinstance(item, dict) and str(item.get("url", "")).strip()
    ]


def extract_reference_urls_from_source(
    source_text: str,
    *,
    source_label: str,
    model: str,
    module_name: str = "",
) -> tuple[list[dict[str, str]], str, str]:
    """1 ソースから参考サイト URL を LLM で抽出する。

    引数: source_text — ヒアリング本文/アポメモ/営業メモ等のテキスト
          source_label — プロンプトに埋め込むソース名
          model — Claude CLI の --model 値
    処理: プロンプトテンプレートに SOURCE_LABEL・SOURCE_TEXT を埋め込み、
          Claude CLI 単発で呼び出して JSON をパース
    出力: (parsed_urls, raw_output, prompt) — パース済みリスト・生出力・使用プロンプト
    """
    tmpl = _load_url_extract_template(module_name=module_name)
    prompt = subst(
        tmpl,
        module_name=module_name,
        SOURCE_LABEL=source_label,
        SOURCE_TEXT=source_text,
    )
    raw_output = generate_text(prompt, model=model, module_name=module_name)
    urls = _parse_url_extraction_response(raw_output)
    return urls, raw_output, prompt


def run_reference_url_extraction(
    *,
    hearing_text: str,
    appo_memo: str,
    sales_notes: str,
    model: str,
    module_name: str = "",
) -> tuple[str, list[dict[str, str]], dict[str, str], dict[str, str]]:
    """3 ソースから参考サイト URL を逐次抽出し、プロンプト用ブロック文字列を返す。

    引数: hearing_text / appo_memo / sales_notes — 各ソーステキスト
          model — Claude CLI の --model
    処理: 非空のソースごとに extract_reference_urls_from_source を逐次呼び出し
    出力: (block_text, all_urls, raw_outputs, raw_prompts)
          raw_outputs / raw_prompts のキー: step_url_hearing / step_url_appo / step_url_sales
    """
    all_urls: list[dict[str, str]] = []
    raw_outputs: dict[str, str] = {}
    raw_prompts: dict[str, str] = {}

    sources = [
        ("step_url_hearing", hearing_text, "ヒアリングシート"),
        ("step_url_appo", appo_memo, "アポ録画メモ"),
        ("step_url_sales", sales_notes, "営業共有事項"),
    ]
    for key, text, label in sources:
        if not (text or "").strip():
            continue
        logger.info("%s 参考サイトURL抽出（%s）…", module_name, label)
        urls, raw, prompt = extract_reference_urls_from_source(
            text, source_label=label, model=model, module_name=module_name,
        )
        all_urls.extend(urls)
        raw_outputs[key] = raw
        raw_prompts[key] = prompt

    return reference_url_block_from_extracted(all_urls), all_urls, raw_outputs, raw_prompts


def reference_url_block_from_extracted(urls: list[dict[str, str]]) -> str:
    """LLM 抽出済み URL リストをプロンプト埋め込み用テキストに整形。"""
    if not urls:
        return "（参考サイトURLの記載なし。手順1-3およびヒアリング本文を参照）"
    seen: set[str] = set()
    lines: list[str] = []
    for item in urls:
        u = item["url"]
        if u in seen:
            continue
        seen.add(u)
        intent = item.get("design_intent", "参考サイト")
        lines.append(f"- {u}（{intent}）")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Manus リファクタブロック（4パイプラインで共通の ~30 行パターン）
# ---------------------------------------------------------------------------


def run_manus_refactor_block(
    *,
    canvas_markdown: str,
    partner_name: str,
    record_number: str,
    work_branch: ContractWorkBranch,
    manual_meta_key: str,
    model: str,
    steps: dict,
    step_prompts: dict,
    hearing_reference_block: str,
    contract_max_pages: int,
    preface_dir: Path | None = None,
) -> tuple[str, str | None, str]:
    """Manus リファクタの共通フロー。

    引数: Claude チェーン完了後の canvas / 案件メタ / チェックポイント保存用の steps 等
    処理: pre_manus チェックポイント書き出し → Manus プロンプト組み立て → Manus タスク実行
    出力: (refactored_md, manus_deploy_github_url, manus_refactor_prompt)
          呼び出し元が outs に代入する
    """
    from modules.basic_lp_refactor_claude import (
        build_basic_lp_refactor_user_prompt,
        run_basic_lp_refactor_stage,
    )
    from modules.llm.llm_raw_output import write_pre_manus_llm_checkpoint

    write_pre_manus_llm_checkpoint(
        site_name=f"{partner_name}-{record_number}",
        work_branch=work_branch,
        manual_meta_key=manual_meta_key,
        model=model,
        steps=dict(steps),
        step_prompts=dict(step_prompts),
        canvas_markdown=canvas_markdown,
        partner_name=partner_name,
        record_number=record_number,
    )

    refactor_kw: dict[str, Any] = dict(
        partner_name=partner_name,
        record_number=record_number,
        hearing_reference_block=hearing_reference_block,
        contract_max_pages=contract_max_pages,
    )
    if preface_dir is not None:
        refactor_kw["preface_dir"] = preface_dir

    prompt = build_basic_lp_refactor_user_prompt(canvas_markdown, **refactor_kw)
    md, manus_deploy_github_url = run_basic_lp_refactor_stage(
        canvas_source_code=canvas_markdown, model=model, **refactor_kw,
    )

    return md, manus_deploy_github_url, prompt
