"""Canvas 由来ソースを Next.js App Router 用にリファクタ（Manus API・タスク1件）。

Manus 向け文言は **`config/prompts/manus/*.txt` に集約**。コードは読み込み・
`{{MANUS_REPO_*}}` / `MANUS_DEPLOY_GITHUB_REPO_HINT` の差し替え・Canvas ブロックの連結のみ。
`MANUS_PROVIDES_DEPLOY_GITHUB_URL` が off のときは `bot_deploy_instruction.txt` を連結しない。

``preface_dir`` は互換のため引数に残すが、Manus プロンプト組み立てでは使用しない（手作業ではプラン別 intro を使わない）。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from config.config import (
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
        f"- 契約ページ数（厳守）: {cap}。"
        " コンテンツ用の App Router の `app/**/page.tsx` および `src/app/**/page.tsx` の合計本数は **"
        f"ちょうど {cap} 本**とすること。**超過も不足も禁止**（パイプラインのビルド検証で不一致は失敗する）。\n"
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


def run_basic_lp_refactor_stage(
    *,
    canvas_source_code: str,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
    record_number: str | None = None,
    hearing_reference_block: str | None = None,
    contract_max_pages: int | None = None,
) -> tuple[str, str | None]:
    """
    Manus にリファクタ用プロンプトを送り、完了まで待つ。

    Returns:
        (フェンス付きマークダウン本文, 任意の GitHub clone URL)。
        ``MANUS_PROVIDES_DEPLOY_GITHUB_URL`` のとき、``BOT_DEPLOY_GITHUB_URL:`` 行（後続に別文があっても可）または
        本文中の ``https://github.com/...git`` を推定して URL を返し、可能なら本文から当該行を除く。
    """
    from modules.manus_refactor import (
        infer_manus_github_clone_url,
        run_manus_refactor_stage,
        split_manus_response_deploy_url,
    )

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
    md, url = split_manus_response_deploy_url(raw)
    if not url:
        url = infer_manus_github_clone_url(raw, record_number=record_number)
        if url:
            logger.warning(
                "Manus 返答に BOT_DEPLOY_GITHUB_URL 行が無いか欠損のため、"
                "本文中の GitHub clone URL をレコード等で推定しました: %s",
                url,
            )
    if url:
        u = url.rstrip("/")
        if not u.lower().endswith(".git"):
            u = f"{u}.git"
        return md, u
    logger.warning(
        "MANUS_PROVIDES_DEPLOY_GITHUB_URL=true だが Manus 返答から deploy URL を取得できませんでした。"
        " 従来どおりボットがローカルから GitHub に push します。",
    )
    return raw, None
