"""案件単位で ``output/<record_number>/llm_steps/`` に LLM 入出力を都度保存する。

引数: ``begin_case_llm_trace(record_number)`` でルートを contextvars にセットする。
処理: TEXT_LLM（Claude Code CLI）は ``modules.claude_manual_common`` の CLI 呼び出しから ``record_llm_turn`` を記録。
      Manus は ``manus_refactor`` 内で ``record_llm_turn`` を明示呼び出し。
出力: ``{seq:03d}_{kind}/input.md`` と ``output.md``（失敗時は ``error.txt``）。
"""
from __future__ import annotations

import logging
import re
from contextvars import ContextVar
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_trace_root: ContextVar[Path | None] = ContextVar("llm_trace_root", default=None)
_step_seq: ContextVar[int] = ContextVar("llm_trace_step_seq", default=0)

_generating_wrap_installed = False


def _safe_segment(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())[:120]
    return s or "unnamed"


def _sanitize_record_folder(record_number: str) -> str:
    raw = str(record_number or "").strip()
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw)[:120]
    return s or "no_record"


def ensure_case_trace_dir(record_number: str) -> Path:
    """``OUTPUT_DIR/<record>/`` と ``llm_steps/`` を作成して返す。"""
    from config.config import OUTPUT_DIR

    root = (OUTPUT_DIR / _sanitize_record_folder(record_number)).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "llm_steps").mkdir(parents=True, exist_ok=True)
    return root


def begin_case_llm_trace(record_number: str) -> Path:
    """トレース対象案件を開始（ステップ番号を 0 にリセット）。"""
    root = ensure_case_trace_dir(record_number)
    _trace_root.set(root)
    _step_seq.set(0)
    return root


def end_case_llm_trace() -> None:
    """トレースを無効化（次案件で再 begin するまで記録しない）。"""
    _trace_root.set(None)


def _next_seq() -> int:
    n = _step_seq.get() + 1
    _step_seq.set(n)
    return n


def _write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(normalized, encoding="utf-8")


def record_llm_turn(
    *,
    kind: str,
    input_text: str,
    output_text: str | None = None,
    error_text: str | None = None,
) -> None:
    """
    アクティブな案件トレースがあるときだけ、1 ステップ分をディスクへ書く。

    出力: ``<root>/llm_steps/<NNN>_<kind>/input.md`` + ``output.md`` または ``error.txt``
    """
    root = _trace_root.get()
    if root is None:
        return
    try:
        seq = _next_seq()
        step_dir = root / "llm_steps" / f"{seq:03d}_{_safe_segment(kind)}"
        step_dir.mkdir(parents=True, exist_ok=True)
        _write_text_file(step_dir / "input.md", input_text or "")
        if error_text is not None:
            _write_text_file(step_dir / "error.txt", error_text)
        elif output_text is not None:
            _write_text_file(step_dir / "output.md", output_text)
        try:
            from config.config import OUTPUT_DIR

            rel = step_dir.resolve().relative_to(OUTPUT_DIR.resolve())
        except ValueError:
            rel = step_dir
        logger.info(
            "LLM トレース保存（1 呼び出しにつき 1 ディレクトリ）: %s",
            rel,
        )
    except Exception:
        logger.exception(
            "modules.llm.llm_step_trace: LLM トレース保存に失敗しました（本処理は継続）"
        )


def install_generative_model_trace_wrap() -> None:
    """後方互換のため残すが、Claude 移行後は何もしない（トレースは共通ヘルパー内で直接呼び出す）。"""
    global _generating_wrap_installed
    if _generating_wrap_installed:
        return
    _generating_wrap_installed = True
    logger.info(
        "LLM ステップトレース有効（Claude: claude_manual_common 内で record_llm_turn を直接呼び出し）"
    )
