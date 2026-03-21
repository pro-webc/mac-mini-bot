"""Canvas 由来ソースを Next.js App Router 用にリファクタ（Gemini・新規チャット1回）。

``preface_dir`` で ``preface_intro.txt`` を切り替え（BASIC LP / BASIC-CP / STANDARD-CP / ADVANCE-CP）、
``preface_shared.txt`` と ``refactoring_instruction.txt`` はいずれも
``config/prompts/basic_lp_refactor/`` を共用する。
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from modules.gemini_generative_timeout import ensure_gemini_rpc_patch_from_config

logger = logging.getLogger(__name__)

_REF_DIR = Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_lp_refactor"
# BASIC-CP 用 ``preface_intro.txt``（共通部は ``basic_lp_refactor/preface_shared.txt``）
BASIC_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "basic_cp_refactor"
)
STANDARD_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "standard_cp_refactor"
)
ADVANCE_CP_REFACTOR_PREFACE_DIR = (
    Path(__file__).resolve().parent.parent / "config" / "prompts" / "advance_cp_refactor"
)

# マニュアル本編に加え、リファクタは「新規チャット」1セッション・generate 1回
BASIC_LP_REFACTOR_GEMINI_API_CALLS = 1


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"modules.basic_lp_refactor_gemini: プロンプトが見つかりません: {path}"
        )
    return path.read_text(encoding="utf-8")


def _build_refactor_preface(*, intro_dir: Path) -> str:
    """
    ``preface_intro.txt``（プラン別）+ ``basic_lp_refactor/preface_shared.txt``（LP / BASIC-CP / STANDARD-CP / ADVANCE-CP 共通）を結合する。
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
) -> str:
    """
    リファクタ指示書 + 元ソース（手順8 / 手順7-3 の成果物）を1つのユーザーメッセージにまとめる。

    Args:
        preface_dir: ``preface_intro.txt`` を読むディレクトリ。未指定時は ``basic_lp_refactor``。
        ``refactoring_instruction.txt`` と ``preface_shared.txt`` は常に ``basic_lp_refactor/`` を参照する。
    """
    src = (canvas_source_code or "").strip()
    if not src:
        raise RuntimeError(
            "modules.basic_lp_refactor_gemini: リファクタリング元ソースが空です。"
        )
    intro_dir = preface_dir or _REF_DIR
    pre = _build_refactor_preface(intro_dir=intro_dir)
    body = _read(_REF_DIR / "refactoring_instruction.txt")
    return (
        pre
        + "\n\n"
        + body
        + "\n\n===== BEGIN_CANVAS_SOURCE =====\n"
        + src
        + "\n===== END_CANVAS_SOURCE =====\n"
    )


def run_basic_lp_refactor_stage(
    *,
    canvas_source_code: str,
    model: Any,
    generation_config: dict[str, Any],
    response_text_fn: Callable[[Any], str],
    preface_dir: Path | None = None,
) -> str:
    """
    新規チャット相当で1回 ``generate_content`` する。

    Args:
        model: 既に設定済みの ``GenerativeModel``
        generation_config: ベース設定（max_output_tokens を広げる）
        response_text_fn: ``basic_lp_gemini_manual._response_text`` を注入（循環 import 回避）
    """
    prompt = build_basic_lp_refactor_user_prompt(
        canvas_source_code, preface_dir=preface_dir
    )
    gcfg = dict(generation_config)
    gcfg["max_output_tokens"] = min(32768, max(int(gcfg.get("max_output_tokens", 8192)), 16384))
    if preface_dir == ADVANCE_CP_REFACTOR_PREFACE_DIR:
        _branch = "ADVANCE-CP"
    elif preface_dir == STANDARD_CP_REFACTOR_PREFACE_DIR:
        _branch = "STANDARD-CP"
    elif preface_dir == BASIC_CP_REFACTOR_PREFACE_DIR:
        _branch = "BASIC-CP"
    else:
        _branch = "BASIC LP"
    logger.info(
        "%s Gemini: リファクタ段階（共通 refactoring_instruction・新規チャット1回・API %s 回）… max_output_tokens=%s",
        _branch,
        BASIC_LP_REFACTOR_GEMINI_API_CALLS,
        gcfg.get("max_output_tokens"),
    )
    ensure_gemini_rpc_patch_from_config()
    resp = model.generate_content(prompt, generation_config=gcfg)
    return response_text_fn(resp)
