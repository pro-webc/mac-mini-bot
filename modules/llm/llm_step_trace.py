"""案件単位で ``output/<record_number>/llm_steps/`` に LLM 入出力を都度保存する。

引数: ``begin_case_llm_trace(record_number)`` でルートを contextvars にセットする。
処理: Gemini は ``GenerativeModel.generate_content`` のラッパーから、
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
    except Exception:
        logger.exception(
            "modules.llm.llm_step_trace: LLM トレース保存に失敗しました（本処理は継続）"
        )


def _stringify_gemini_contents(contents: Any) -> str:
    if contents is None:
        return ""
    if isinstance(contents, str):
        return contents
    if isinstance(contents, (list, tuple)):
        parts_out: list[str] = []
        for i, item in enumerate(contents):
            parts_out.append(f"--- content[{i}] ---\n{_stringify_one_content_part(item)}")
        return "\n".join(parts_out)
    return _stringify_one_content_part(contents)


def _stringify_one_content_part(c: Any) -> str:
    role = getattr(c, "role", None)
    parts = getattr(c, "parts", None)
    if parts is None:
        return str(c)
    texts: list[str] = []
    for p in parts:
        t = getattr(p, "text", None)
        if t:
            texts.append(str(t))
        else:
            texts.append(f"(non-text part: {type(p).__name__})")
    body = "\n".join(texts)
    if role:
        return f"role={role}\n{body}"
    return body


def _response_text_safe(response: Any) -> str:
    try:
        if not getattr(response, "candidates", None):
            return (
                "(no candidates) "
                f"prompt_feedback={getattr(response, 'prompt_feedback', None)!r}"
            )
        chunks: list[str] = []
        for cand in response.candidates:
            content = getattr(cand, "content", None)
            if not content or not getattr(content, "parts", None):
                continue
            for part in content.parts:
                t = getattr(part, "text", None)
                if t:
                    chunks.append(t)
        out = "".join(chunks).strip()
        return out if out else "(empty assistant text)"
    except Exception as e:
        return f"(response extract error: {e})"


def install_generative_model_trace_wrap() -> None:
    """
    ``GenerativeModel.generate_content`` をラップし、トレース有効時に入出力を保存する。

    ``ensure_gemini_rpc_patch_from_config`` の **後**（タイムアウトラッパーの外側）で 1 回だけ連鎖する。
    """
    global _generating_wrap_installed
    if _generating_wrap_installed:
        return
    from google.generativeai import generative_models as gm

    inner = gm.GenerativeModel.generate_content

    def generate_content_traced(
        self: Any,
        contents: Any,
        *,
        generation_config: Any = None,
        safety_settings: Any = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        resp = inner(
            self,
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=stream,
            **kwargs,
        )
        if _trace_root.get() is not None and not stream:
            try:
                inp = _stringify_gemini_contents(contents)
                out = _response_text_safe(resp)
                record_llm_turn(
                    kind="gemini_generate_content",
                    input_text=inp,
                    output_text=out,
                )
            except Exception:
                logger.exception(
                    "modules.llm.llm_step_trace: Gemini トレース記録で例外（応答はそのまま返す）"
                )
        return resp

    gm.GenerativeModel.generate_content = generate_content_traced  # type: ignore[method-assign]
    _generating_wrap_installed = True
    logger.info(
        "Gemini generate_content に LLM ステップトレースを連鎖（output/<record>/llm_steps/）"
    )
