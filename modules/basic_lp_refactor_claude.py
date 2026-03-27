"""Canvas 由来ソースを Next.js App Router 用にリファクタ（Manus API・タスク1件）。

Manus 向け文言は **`config/prompts/manus/*.txt` に集約**。コードは読み込み・
`{{MANUS_REPO_*}}` / `MANUS_DEPLOY_GITHUB_REPO_HINT` の差し替え・Canvas ブロックの連結のみ。
`MANUS_PROVIDES_DEPLOY_GITHUB_URL` が off のときは `bot_deploy_instruction.txt` を連結しない。

``preface_dir`` は互換のため引数に残すが、Manus プロンプト組み立てでは使用しない（手作業ではプラン別 intro を使わない）。
"""
from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

import json

from config.config import (
    CLAUDE_BASIC_LP_MODEL,
    GITHUB_USERNAME,
    MANUS_DEPLOY_GITHUB_REPO_HINT,
    MANUS_PROVIDES_DEPLOY_GITHUB_URL,
)
from modules.github_client import sanitize_github_repo_name

logger = logging.getLogger(__name__)

_CANVAS_CODE_BLOCK_RE = re.compile(
    r"```(?:tsx|jsx|typescript|javascript|ts|js)?\s*\n(.*?)```",
    re.IGNORECASE | re.DOTALL,
)

_MANUS_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "manus"
# ``run_manus_refactor_stage`` のログ用（中身の .txt は読まない）
BASIC_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_cp_refactor"
)
STANDARD_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "standard_cp_refactor"
)
ADVANCE_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "advance_cp_refactor"
)

# リファクタは Manus ``POST /v1/tasks`` 相当を 1 件（ポーリングは内部）
BASIC_LP_REFACTOR_MANUS_TASKS = 1


def manus_repo_name_for_prompt(
    record_number: str | None,
    partner_name: str | None,
) -> str:
    """Manus 手順1: リポジトリ名 ``{レコード番号}-{ASCII部分}``（GitHub 向けに正規化済み）。"""
    return sanitize_github_repo_name(
        (partner_name or "").strip() or "unknown",
        str(record_number or "").strip() or "0",
    )


def manus_repo_description_for_prompt(
    partner_name: str | None,
    record_number: str | None = None,
) -> str:
    """Manus 手順1: ディスクリプション ``{レコード番号} {パートナー名}``（スプレッドシートそのまま）。

    GitHub の description 上限（350 文字）で切り詰める。
    """
    rec = (str(record_number) if record_number else "").strip()
    pn = (partner_name or "").strip() or "先方名未設定"
    desc = f"{rec} {pn}" if rec else pn
    if len(desc) > 350:
        desc = desc[:350]
    return desc


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"modules.basic_lp_refactor_claude: プロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def _looks_like_canvas_source(code: str) -> bool:
    """Claude CLI 出力中のコードフェンスから、React/TSX 本文らしいものを拾う。"""
    s = (code or "").strip()
    if not s:
        return False
    hints = (
        "className=",
        "export default",
        "useState(",
        "useEffect(",
        "return (",
        "</",
        "from 'react'",
        'from "react"',
    )
    return any(h in s for h in hints)


def _normalize_canvas_source_for_manus(canvas_source_code: str) -> str:
    """Manus に渡す前に説明文を除き、Canvas の実コード本文だけに整える。"""
    src = (canvas_source_code or "").strip()
    if not src:
        raise RuntimeError(
            "modules.basic_lp_refactor_claude: リファクタリング元ソースが空です。"
        )
    blocks = [
        m.group(1).strip()
        for m in _CANVAS_CODE_BLOCK_RE.finditer(src)
        if _looks_like_canvas_source(m.group(1))
    ]
    if blocks:
        return max(blocks, key=len)
    if src.startswith("```") and src.endswith("```"):
        first_nl = src.find("\n")
        if first_nl != -1:
            body = src[first_nl + 1 :].rstrip()
            if body.endswith("```"):
                return body[: -3].rstrip()
    return src


def _manus_contract_pages_and_legal_block(contract_max_pages: int | None) -> str:
    """Manus に契約ページ数と法的情報（モーダル表示）を明示するブロック。"""
    if contract_max_pages is None:
        return ""
    cap = int(contract_max_pages)
    multi = cap > 1
    multi_line = ""
    if multi:
        multi_line = (
            f"- 契約が複数ページ（{cap}）のときは、元 Canvas に `useState` 等の擬似ページ切替が無くても、"
            " **Pattern A（`app/page.tsx` のみの縦スクロール単一路線）にしてはならない**。"
            " 見出し・ナビ・セクション境界・コメントから各論理ページを切り出し、"
            " **ファイルベースルーティングでちょうど上記本数の `page.tsx` に分配**すること。\n"
        )
    return (
        "\n\n---\n\n"
        "【契約ページ数・法的情報（必須・最優先の制約）】\n"
        f"- 契約ページ数（厳守）: **{cap}**。"
        " コンテンツ用の App Router の `app/**/page.tsx` および `src/app/**/page.tsx` の合計本数は **"
        f"ちょうど {cap} 本**とすること。**超過も不足も禁止**（パイプラインのビルド検証で不一致は即失敗する）。\n"
        f"- **元コードに存在しないページの `page.tsx` を新規作成することは禁止**。"
        " 特に `blog/page.tsx`・`news/page.tsx`・`privacy/page.tsx`・`terms/page.tsx` 等を"
        " 元コードに対応するセクションがないのに追加してはならない。"
        " 元コードのページ構成をそのまま App Router のルーティングに変換し、"
        f" **合計 {cap} 本に一致させること**。\n"
        + multi_line
        + "- プライバシーポリシー・利用規約などの法的情報は **契約ページ数に含めない**。"
        " **独立の `page.tsx`（例: `app/privacy/page.tsx`）を新規作成しない**。\n"
        "- これらは **既存のいずれかのページ上**で `Dialog` / `Sheet` / `Drawer` / `<details>` 等の UI で全文表示する。"
        " フッターからは **同一ページ内で開く `button` またはモーダル起動**とし、**/privacy 等の別 URL への `Link` を新設しない**。\n"
    )


def build_basic_lp_refactor_user_prompt(
    canvas_source_code: str,
    *,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
    record_number: str | None = None,
    hearing_reference_block: str | None = None,
    contract_max_pages: int | None = None,
) -> str:
    """
    手作業 Manus マニュアルと同じオーケストレーション + リファクタ指示書 + Canvas。

    Args:
        canvas_source_code: Claude Canvas 単一ファイル相当。
        preface_dir: 未使用（シグネチャ互換）。
        partner_name: 制作スプレッドシートの「パートナー名」列（プロンプト上の先方名と同一）。
        record_number: 制作スプレッドシートのレコード番号（リポジトリ名・ディスクリプション用）。
        hearing_reference_block: 任意。ヒアリング由来の参考サイト・デザイン原文（Canvas 直前に再掲）。
        contract_max_pages: 任意。契約プランのページ数。指定時はリファクタで余分な ``page.tsx`` を増やさない旨を注入する。
    """
    del preface_dir  # Manus 手作業フローではプラン別 preface を使わない
    src = _normalize_canvas_source_for_manus(canvas_source_code)
    repo_name = manus_repo_name_for_prompt(record_number, partner_name)
    repo_desc = manus_repo_description_for_prompt(partner_name, record_number)
    orch = _read(_MANUS_DIR / "orchestration_prompt.txt")
    orch = orch.replace("{{MANUS_REPO_NAME}}", repo_name).replace(
        "{{MANUS_REPO_DESCRIPTION}}", repo_desc
    )
    refactor = _read(_MANUS_DIR / "refactoring_instruction_handwork.txt")
    legal = _manus_contract_pages_and_legal_block(contract_max_pages)
    hr = (hearing_reference_block or "").strip()
    hr_block = ("\n\n---\n\n" + hr) if hr else ""

    base = (
        orch
        + "\n\n---\n\n"
        + refactor
        + legal
        + hr_block
        + "\n\n===== BEGIN_CANVAS_SOURCE =====\n"
        + "以下がリファクタリング元のソースコードです。"
        + " 外部ファイルの添付や参照ではなく、このブロック内のコードを直接入力として扱ってください。\n\n"
        + "```tsx\n"
        + src
        + "\n```\n===== END_CANVAS_SOURCE =====\n"
    )
    if MANUS_PROVIDES_DEPLOY_GITHUB_URL:
        base += "\n\n" + _manus_bot_deploy_instruction_block()
    return base


def _manus_bot_deploy_instruction_block() -> str:
    """`bot_deploy_instruction.txt` を読み、任意で `bot_deploy_repo_hint_line.txt` を差し込む。"""
    body = _read(_MANUS_DIR / "bot_deploy_instruction.txt")
    hint = (MANUS_DEPLOY_GITHUB_REPO_HINT or "").strip()
    if hint:
        line = _read(_MANUS_DIR / "bot_deploy_repo_hint_line.txt").replace(
            "{{MANUS_DEPLOY_GITHUB_REPO_HINT}}", hint
        )
        hint_line = "\n" + line
    else:
        hint_line = ""
    return body.replace("{{MANUS_DEPLOY_GITHUB_REPO_HINT_LINE}}", hint_line)


# ---------------------------------------------------------------------------
# Manus 返答を Claude CLI で検証・状況判断・リカバリ判断
# ---------------------------------------------------------------------------

_COMMON_PROMPT_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "common"

_NORMALIZED_URL_RE = re.compile(
    r"https://github\.com/[\w.%-]+/[\w.%-]+\.git",
    re.IGNORECASE,
)


class PostManusResult:
    """post_manus_verify の構造化結果。"""
    __slots__ = ("status", "github_url", "completed_steps", "diagnosis", "recovery", "recovery_url")

    def __init__(
        self,
        *,
        status: str = "FAILED",
        github_url: str | None = None,
        completed_steps: list[str] | None = None,
        diagnosis: str = "",
        recovery: str = "PROCEED",
        recovery_url: str | None = None,
    ):
        self.status = status
        self.github_url = github_url
        self.completed_steps = completed_steps or []
        self.diagnosis = diagnosis
        self.recovery = recovery
        self.recovery_url = recovery_url

    def __repr__(self) -> str:
        return (
            f"PostManusResult(status={self.status!r}, github_url={self.github_url!r}, "
            f"recovery={self.recovery!r}, diagnosis={self.diagnosis!r})"
        )


def _verify_manus_response_via_claude_cli(
    manus_response: str,
    *,
    record_number: str | None = None,
    partner_name: str | None = None,
    expected_repo_name: str | None = None,
    model: str | None = None,
) -> PostManusResult:
    """Manus 応答を Claude CLI で分析し、状況判断・リカバリ方針を含む構造化結果を返す。

    引数: manus_response — Manus 完了後の返答テキスト全文
          record_number / partner_name — 案件特定用
          expected_repo_name — Manus に指示したリポジトリ名
          model — Claude CLI の --model
    処理: post_manus_verify.txt に応答を埋め込み、Claude CLI 単発で呼び出し、
          JSON レスポンスをパースして PostManusResult を構築
    出力: PostManusResult（status / github_url / recovery 等を含む）
    """
    from modules.claude_manual_common import generate_text, load_step, subst

    tmpl = load_step(
        _COMMON_PROMPT_DIR, "post_manus_verify.txt",
        module_name="basic_lp_refactor_claude",
    )
    repo_name = expected_repo_name or ""
    if not repo_name and record_number and partner_name:
        repo_name = sanitize_github_repo_name(partner_name, record_number)
    github_owner = (GITHUB_USERNAME or "").strip()

    prompt = subst(
        tmpl,
        module_name="basic_lp_refactor_claude",
        RECORD_NUMBER=str(record_number or ""),
        PARTNER_NAME=str(partner_name or ""),
        EXPECTED_REPO_NAME=repo_name,
        GITHUB_OWNER=github_owner,
        MANUS_RESPONSE=manus_response,
    )
    cli_model = (model or CLAUDE_BASIC_LP_MODEL).strip()
    try:
        raw = generate_text(
            prompt, model=cli_model,
            module_name="basic_lp_refactor_claude(post-Manus検証)",
        )
    except Exception:
        logger.warning(
            "Claude CLI による post-Manus 検証に失敗しました（正規表現フォールバックに移行）",
            exc_info=True,
        )
        return _fallback_post_manus_result(manus_response, record_number=record_number)

    return _parse_post_manus_json(raw, manus_response, record_number=record_number)


def _parse_post_manus_json(
    cli_output: str, manus_response: str, *, record_number: str | None = None,
) -> PostManusResult:
    """Claude CLI 出力から JSON を抽出してパースする。失敗時は正規表現フォールバック。"""
    text = (cli_output or "").strip()
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    if json_start >= 0 and json_end > json_start:
        try:
            d = json.loads(text[json_start:json_end])
            url = (d.get("github_url") or d.get("recovery_url") or "")
            if url and not _NORMALIZED_URL_RE.search(url):
                url = None
            recovery = (d.get("recovery") or "PROCEED").upper()
            recovery_url = (d.get("recovery_url") or "")
            if recovery_url and not _NORMALIZED_URL_RE.search(recovery_url):
                recovery_url = None
            return PostManusResult(
                status=(d.get("status") or "FAILED").upper(),
                github_url=url or None,
                completed_steps=d.get("completed_steps") or [],
                diagnosis=d.get("diagnosis") or "",
                recovery=recovery,
                recovery_url=recovery_url or None,
            )
        except (json.JSONDecodeError, TypeError):
            logger.warning("post-Manus 検証の JSON パースに失敗。正規表現フォールバック。")

    return _fallback_post_manus_result(manus_response, record_number=record_number)


def _fallback_post_manus_result(
    manus_response: str, *, record_number: str | None = None,
) -> PostManusResult:
    """Claude CLI が使えないときの正規表現ベースフォールバック。"""
    from modules.manus_refactor import (
        infer_manus_github_clone_url,
        split_manus_response_deploy_url,
    )
    _, url = split_manus_response_deploy_url(manus_response)
    if not url:
        url = infer_manus_github_clone_url(manus_response, record_number=record_number)
    if url:
        u = url.rstrip("/")
        if not u.lower().endswith(".git"):
            u = f"{u}.git"
        return PostManusResult(
            status="SUCCESS", github_url=u, recovery="PROCEED",
            diagnosis="正規表現フォールバックで URL を抽出",
        )
    return PostManusResult(
        status="FAILED", diagnosis="URL 抽出不可（正規表現フォールバック）",
        recovery="LOCAL_PUSH",
    )


def _verify_github_url_reachable(url: str) -> bool:
    """git ls-remote で URL の到達確認を行う（LLM 不要）。

    引数: url — `https://github.com/owner/repo.git` 形式
    処理: git ls-remote --exit-code を実行（タイムアウト 15s）
    出力: True（到達可能） / False（失敗）
    """
    git = shutil.which("git")
    if not git:
        logger.warning("git コマンドが見つかりません。URL 到達確認をスキップします。")
        return True
    try:
        r = subprocess.run(
            [git, "ls-remote", "--exit-code", url, "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            return True
        logger.warning(
            "git ls-remote 失敗 (exit=%d): %s — %s",
            r.returncode, url, (r.stderr or "").strip()[:200],
        )
        return False
    except subprocess.TimeoutExpired:
        logger.warning("git ls-remote がタイムアウトしました: %s", url)
        return False
    except Exception:
        logger.warning("git ls-remote 実行エラー: %s", url, exc_info=True)
        return False


def run_basic_lp_refactor_stage(
    *,
    canvas_source_code: str,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
    record_number: str | None = None,
    hearing_reference_block: str | None = None,
    contract_max_pages: int | None = None,
    model: str | None = None,
) -> tuple[str, str | None]:
    """Manus にリファクタ用プロンプトを送り、完了まで待つ。

    引数: canvas_source_code — Claude CLI 出力の Canvas / record_number — レコード番号
          model — Claude CLI URL 正規化に使うモデル（省略時 CLAUDE_BASIC_LP_MODEL）
    処理: Manus タスク実行 → Claude CLI で検証・状況判断 → git ls-remote で到達確認
          → リカバリ方針に基づいて URL を決定
    出力: (フェンス付きマークダウン本文, GitHub clone URL or None)
    """
    from modules.manus_refactor import (
        run_manus_refactor_stage,
        split_manus_response_deploy_url,
    )

    expected_repo = sanitize_github_repo_name(
        partner_name or "", record_number or "",
    ) if (partner_name or record_number) else ""

    raw = run_manus_refactor_stage(
        canvas_source_code=canvas_source_code,
        preface_dir=preface_dir,
        partner_name=partner_name,
        record_number=record_number,
        hearing_reference_block=hearing_reference_block,
        contract_max_pages=contract_max_pages,
    )
    if not MANUS_PROVIDES_DEPLOY_GITHUB_URL:
        return raw, None

    # --- Claude CLI で Manus 応答を検証・状況判断 ---
    result = _verify_manus_response_via_claude_cli(
        raw,
        record_number=record_number,
        partner_name=partner_name,
        expected_repo_name=expected_repo,
        model=model,
    )
    logger.info("post-Manus 検証: %s", result)

    # --- 検証結果に基づいて URL を決定 ---
    candidate_url = result.github_url

    if result.recovery == "USE_EXISTING_REPO" and not candidate_url:
        candidate_url = result.recovery_url
    if not candidate_url and result.recovery == "USE_EXISTING_REPO" and expected_repo:
        owner = (GITHUB_USERNAME or "").strip()
        if owner:
            candidate_url = f"https://github.com/{owner}/{expected_repo}.git"
            logger.info("既存リポ利用: 期待リポ名から URL を構築: %s", candidate_url)

    if candidate_url and _verify_github_url_reachable(candidate_url):
        logger.info(
            "post-Manus 検証 + git ls-remote で deploy URL を確認: %s (recovery=%s)",
            candidate_url, result.recovery,
        )
        md, _ = split_manus_response_deploy_url(raw)
        return md, candidate_url

    if candidate_url:
        logger.warning(
            "検証で得た URL が git ls-remote で到達不可: %s — ローカル push フォールバック",
            candidate_url,
        )

    if result.recovery == "LOCAL_PUSH":
        logger.info("post-Manus 検証: ローカル push が推奨されました。diagnosis=%s", result.diagnosis)

    logger.warning(
        "Manus 返答から有効な deploy URL を取得できませんでした。"
        " ボットがローカルから GitHub に push します。 diagnosis=%s",
        result.diagnosis,
    )
    return raw, None
