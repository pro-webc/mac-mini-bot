"""LLM の生成テキストを改変せずサイトディレクトリに書き、Git push に含める。

ボットの正本（source of truth）: パーサやビルドが失敗しても、ここに残したテキストが AI の答えの記録になる。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from modules.contract_workflow import ContractWorkBranch

logger = logging.getLogger(__name__)

_RAW_OUTPUT_DIR = "llm_raw_output"
_GEMINI_STEPS_SUBDIR = "gemini_steps"

# プラン別に spec に載りうる LLM 文字列キー（順不同・空はスキップ）
_SPEC_LLM_KEYS: dict[ContractWorkBranch, tuple[str, ...]] = {
    ContractWorkBranch.BASIC_LP: (
        "basic_lp_refactored_source_markdown",
        "basic_lp_manual_gemini_final",
        "basic_lp_manual_gemini_step_4_wireframe",
        "basic_lp_manual_gemini_step_7_design_doc",
    ),
    ContractWorkBranch.BASIC: (
        "basic_refactored_source_markdown",
        "basic_manual_gemini_final",
        "basic_manual_gemini_step_2_structure",
        "basic_manual_gemini_step_6_design_doc",
    ),
    ContractWorkBranch.STANDARD: (
        "standard_refactored_source_markdown",
        "standard_manual_gemini_final",
        "standard_manual_gemini_step_2",
        "standard_manual_gemini_step_6",
    ),
    ContractWorkBranch.ADVANCE: (
        "advance_refactored_source_markdown",
        "advance_manual_gemini_final",
        "advance_manual_gemini_step_2",
        "advance_manual_gemini_step_6",
    ),
}

_MANUAL_META_KEYS = (
    "basic_lp_manual_gemini",
    "basic_cp_manual_gemini",
    "standard_cp_manual_gemini",
    "advance_cp_manual_gemini",
)


def _safe_segment(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())[:120]
    return s or "unnamed"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_llm_raw_artifacts(
    site_dir: Path,
    *,
    spec: dict[str, Any],
    requirements_result: dict[str, Any] | None,
    work_branch: ContractWorkBranch,
) -> int:
    """
    ``site_dir/llm_raw_output/`` 以下に LLM 出力をそのまま保存する。

    - spec 上のプラン別テキストフィールド（.md）
    - requirements_result の ``site_build_prompt``（.txt）
    - ``*_manual_gemini`` メタの ``steps`` 辞書（各ステップ .md）

    Returns:
        書き込んだファイル数
    """
    site_dir = site_dir.resolve()
    root = site_dir / _RAW_OUTPUT_DIR
    n = 0

    for key in _SPEC_LLM_KEYS.get(work_branch, ()):
        raw = spec.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        _write_text(root / f"{_safe_segment(key)}.md", raw)
        n += 1

    if requirements_result:
        prompt = requirements_result.get("site_build_prompt")
        if isinstance(prompt, str) and prompt.strip():
            _write_text(root / "site_build_prompt.txt", prompt)
            n += 1

        for meta_key in _MANUAL_META_KEYS:
            meta = requirements_result.get(meta_key)
            if not isinstance(meta, dict):
                continue
            steps = meta.get("steps")
            if not isinstance(steps, dict):
                continue
            pipe = _safe_segment(meta_key)
            model = meta.get("model")
            if isinstance(model, str) and model.strip():
                _write_text(
                    root / _GEMINI_STEPS_SUBDIR / pipe / "_model.txt",
                    model.strip() + "\n",
                )
                n += 1
            for step_name, step_body in steps.items():
                if not isinstance(step_body, str) or not step_body.strip():
                    continue
                fn = _safe_segment(str(step_name)) + ".md"
                _write_text(
                    root / _GEMINI_STEPS_SUBDIR / pipe / fn,
                    step_body,
                )
                n += 1

    logger.info(
        "LLM 生出力を %s に %s ファイル保存（push に含まれます）",
        root.relative_to(site_dir),
        n,
    )
    return n
