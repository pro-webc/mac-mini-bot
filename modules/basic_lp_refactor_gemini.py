"""Canvas 由来ソースを Next.js App Router 用にリファクタ（Manus API・タスク1件）。

Manus 向けユーザープロンプトは **手作業マニュアルと同じ構成のみ**（`config/prompts/manus/orchestration_prompt.txt` +
`refactoring_instruction_handwork.txt`）＋ Canvas ブロック。ボット専用の追記は付けない。

``preface_dir`` は互換のため引数に残すが、Manus プロンプト組み立てでは使用しない（手作業ではプラン別 intro を使わない）。
"""
from __future__ import annotations

import logging
from pathlib import Path

from config.config import MANUS_DEPLOY_GITHUB_REPO_HINT, MANUS_PROVIDES_DEPLOY_GITHUB_URL

logger = logging.getLogger(__name__)

_REF_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_lp_refactor"
_MANUS_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "manus"
# BASIC-CP 用 ``preface_intro.txt``（Gemini マニュアル側で使用。Manus プロンプトでは未使用）
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


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"modules.basic_lp_refactor_gemini: プロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def _build_refactor_preface(*, intro_dir: Path) -> str:
    """
    ``preface_intro.txt``（プラン別）+ ``basic_lp_refactor/preface_shared.txt``（LP / BASIC-CP / STANDARD-CP / ADVANCE-CP 共通）を結合する。

    Manus 向け ``build_basic_lp_refactor_user_prompt`` では未使用。Gemini 等の他用途向けに残す。
    """
    intro_p = intro_dir / "preface_intro.txt"
    shared_p = _REF_DIR / "preface_shared.txt"
    if intro_p.is_file() and shared_p.is_file():
        return _read(intro_p).rstrip() + "\n\n" + _read(shared_p).rstrip() + "\n"
    legacy = intro_dir / "preface.txt"
    if legacy.is_file():
        return _read(legacy)
    raise RuntimeError(
        "modules.basic_lp_refactor_gemini: preface_intro.txt + preface_shared.txt、"
        f"または preface.txt が必要です: {intro_dir}"
    )


def build_basic_lp_refactor_user_prompt(
    canvas_source_code: str,
    *,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
) -> str:
    """
    手作業 Manus マニュアルと同じオーケストレーション + リファクタ指示書 + Canvas。

    Args:
        canvas_source_code: Gemini Canvas 単一ファイル相当。
        preface_dir: 未使用（シグネチャ互換）。
        partner_name: 制作シートの先方名（オーケストレーション手順1の Description 用）。
    """
    del preface_dir  # Manus 手作業フローではプラン別 preface を使わない
    src = (canvas_source_code or "").strip()
    if not src:
        raise RuntimeError(
            "modules.basic_lp_refactor_gemini: リファクタリング元ソースが空です。"
        )
    pn = (partner_name or "").strip() or "先方名未設定"
    orch = _read(_MANUS_DIR / "orchestration_prompt.txt").replace("{{PARTNER_NAME}}", pn)
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
        base += "\n\n" + _manus_github_deploy_instruction_block()
    return base


def _manus_github_deploy_instruction_block() -> str:
    """MANUS_PROVIDES_DEPLOY_GITHUB_URL 時に Manus へ付与する追記（手作業フロー: push → Vercel に URL）。"""
    hint = (MANUS_DEPLOY_GITHUB_REPO_HINT or "").strip()
    hint_line = (
        f"\n- push 先の推奨リポジトリ（可能ならこの名前で作成・更新）: `{hint}`（GitHub 上は `https://github.com/{hint}.git` 形式）"
        if hint
        else ""
    )
    return (
        "## 手作業フローとの整合（mac-mini-bot が Vercel に渡す Git URL）\n\n"
        "リファクタ結果のソースを **あなたの環境で GitHub に push** したうえで、返答本文の **最後の非空行** を次の形式の **1 行だけ** にすること（この行より後に文字を書かない）:\n\n"
        "`BOT_DEPLOY_GITHUB_URL: https://github.com/オーナー/リポジトリ.git`\n\n"
        "- 上記1行は **フェンス外**。**それより前**は従来どおり「1ファイル=1フェンス」のマークダウンのみ（パース規則は変えない）。\n"
        "- push したコミットの内容は、直前のフェンス群と **同一** にすること（ボットはローカルにも同じフェンスを適用し `npm build` する）。"
        + hint_line
    )


def run_basic_lp_refactor_stage(
    *,
    canvas_source_code: str,
    preface_dir: Path | None = None,
    partner_name: str | None = None,
) -> tuple[str, str | None]:
    """
    Manus にリファクタ用プロンプトを送り、完了まで待つ。

    Returns:
        (フェンス付きマークダウン本文, 任意の GitHub clone URL)。
        ``MANUS_PROVIDES_DEPLOY_GITHUB_URL`` かつ末尾に ``BOT_DEPLOY_GITHUB_URL:`` があるとき URL を返し、本文からその行を除く。
    """
    from modules.manus_refactor import (
        run_manus_refactor_stage,
        split_manus_response_deploy_url,
    )

    raw = run_manus_refactor_stage(
        canvas_source_code=canvas_source_code,
        preface_dir=preface_dir,
        partner_name=partner_name,
    )
    if not MANUS_PROVIDES_DEPLOY_GITHUB_URL:
        return raw, None
    md, url = split_manus_response_deploy_url(raw)
    if url:
        return md, url
    logger.warning(
        "MANUS_PROVIDES_DEPLOY_GITHUB_URL=true だが Manus 返答末尾に %s 行がありません。"
        " 従来どおりボットがローカルから GitHub に push します。",
        "BOT_DEPLOY_GITHUB_URL:",
    )
    return raw, None
