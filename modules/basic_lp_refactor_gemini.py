"""Canvas 由来ソースを Next.js App Router 用にリファクタ（Manus API・タスク1件）。

Manus 向け文言は **`config/prompts/manus/*.txt` に集約**。コードは読み込み・
`{{MANUS_REPO_*}}` / `MANUS_DEPLOY_GITHUB_REPO_HINT` の差し替え・Canvas ブロックの連結のみ。
`MANUS_PROVIDES_DEPLOY_GITHUB_URL` が off のときは `bot_deploy_instruction.txt` を連結しない。

``preface_dir`` は互換のため引数に残すが、Manus プロンプト組み立てでは使用しない（手作業ではプラン別 intro を使わない）。
"""
from __future__ import annotations

import logging
from pathlib import Path

from config.config import (
    MANUS_DEPLOY_GITHUB_REPO_HINT,
    MANUS_PROVIDES_DEPLOY_GITHUB_URL,
)

logger = logging.getLogger(__name__)

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
    """Manus 手順1: リポジトリ名 ``bot-{レコード番号}-{先方名}``（プレースホルダ展開後のそのまま）。

    先方名は制作スプレッドシートの「パートナー名」列（コード上 ``partner_name``）と同一。
    """
    rec = str(record_number or "").strip() or "0"
    pn = (partner_name or "").strip() or "先方名未設定"
    return f"bot-{rec}-{pn}"


def manus_repo_description_for_prompt(partner_name: str | None) -> str:
    """Manus 手順1: ディスクリプションは常に ``test`` + 先方名（工程テスト・本番共通）。

    先方名は制作スプレッドシートの「パートナー名」列（``partner_name``）と同一。
    """
    pn = (partner_name or "").strip() or "先方名未設定"
    return f"test{pn}"


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"modules.basic_lp_refactor_gemini: プロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def build_basic_lp_refactor_user_prompt(
    canvas_source_code: str,
    *,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
    record_number: str | None = None,
) -> str:
    """
    手作業 Manus マニュアルと同じオーケストレーション + リファクタ指示書 + Canvas。

    Args:
        canvas_source_code: Gemini Canvas 単一ファイル相当。
        preface_dir: 未使用（シグネチャ互換）。
        partner_name: 制作スプレッドシートの「パートナー名」列（プロンプト上の先方名と同一）。
        record_number: 制作スプレッドシートのレコード番号（リポジトリ名 ``bot-{番号}-{先方名}`` 用）。
    """
    del preface_dir  # Manus 手作業フローではプラン別 preface を使わない
    src = (canvas_source_code or "").strip()
    if not src:
        raise RuntimeError(
            "modules.basic_lp_refactor_gemini: リファクタリング元ソースが空です。"
        )
    repo_name = manus_repo_name_for_prompt(record_number, partner_name)
    repo_desc = manus_repo_description_for_prompt(partner_name)
    orch = _read(_MANUS_DIR / "orchestration_prompt.txt")
    orch = orch.replace("{{MANUS_REPO_NAME}}", repo_name).replace(
        "{{MANUS_REPO_DESCRIPTION}}", repo_desc
    )
    refactor = _read(_MANUS_DIR / "refactoring_instruction_handwork.txt")

    base = (
        orch
        + "\n\n---\n\n"
        + refactor
        + "\n\n===== BEGIN_CANVAS_SOURCE =====\n"
        + src
        + "\n===== END_CANVAS_SOURCE =====\n"
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
