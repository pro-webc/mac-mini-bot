"""LLM の生成テキストを改変せずサイトディレクトリに書き、Git push に含める。

ボットの正本（source of truth）: パーサやビルドが失敗しても、ここに残したテキストが AI の答えの記録になる。
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.contract_workflow import ContractWorkBranch

from .llm_text_artifacts import write_llm_yaml_artifact

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
        "manus_deploy_github_url",
    ),
    ContractWorkBranch.BASIC: (
        "basic_refactored_source_markdown",
        "basic_manual_gemini_final",
        "basic_manual_gemini_step_2_structure",
        "basic_manual_gemini_step_6_design_doc",
        "manus_deploy_github_url",
    ),
    ContractWorkBranch.STANDARD: (
        "standard_refactored_source_markdown",
        "standard_manual_gemini_final",
        "standard_manual_gemini_step_2",
        "standard_manual_gemini_step_6",
        "manus_deploy_github_url",
    ),
    ContractWorkBranch.ADVANCE: (
        "advance_refactored_source_markdown",
        "advance_manual_gemini_final",
        "advance_manual_gemini_step_2",
        "advance_manual_gemini_step_6",
        "manus_deploy_github_url",
    ),
}

_MANUAL_META_KEYS = (
    "basic_lp_manual_gemini",
    "basic_cp_manual_gemini",
    "standard_cp_manual_gemini",
    "advance_cp_manual_gemini",
)

# Manus リファクタの入力（Canvas 相当）と出力（フェンス付き MD）の spec キー
_MANUS_BRANCH_KEYS: dict[ContractWorkBranch, tuple[str, str]] = {
    ContractWorkBranch.BASIC_LP: (
        "basic_lp_refactored_source_markdown",
        "basic_lp_manual_gemini_final",
    ),
    ContractWorkBranch.BASIC: (
        "basic_refactored_source_markdown",
        "basic_manual_gemini_final",
    ),
    ContractWorkBranch.STANDARD: (
        "standard_refactored_source_markdown",
        "standard_manual_gemini_final",
    ),
    ContractWorkBranch.ADVANCE: (
        "advance_refactored_source_markdown",
        "advance_manual_gemini_final",
    ),
}

_MANUS_ONLY_TESTS_SUBDIR = "manus_only_tests"


def _safe_segment(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())[:120]
    return s or "unnamed"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(normalized, encoding="utf-8")


def write_llm_raw_artifacts(
    site_dir: Path,
    *,
    spec: dict[str, Any],
    requirements_result: dict[str, Any] | None,
    work_branch: ContractWorkBranch,
) -> int:
    """
    ``site_dir/llm_raw_output/`` 以下に LLM 出力をそのまま保存する。

    - spec 上のプラン別テキストフィールド（Markdown 本文は .md、``manus_deploy_github_url`` のみプレーン URL 用に .txt）
    - requirements_result の ``site_build_prompt``（.txt）
    - ``*_manual_gemini`` メタの ``steps`` 辞書（各ステップ .md）
    - 構造化データの正本 ``requirements_result.yaml`` / ``spec.yaml``（UTF-8 テキスト）

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
        # URL 1 行だけのキーは .md にするとプレビューがリンク化して下線付きになるため .txt にする
        ext = ".txt" if key == "manus_deploy_github_url" else ".md"
        _write_text(root / f"{_safe_segment(key)}{ext}", raw)
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

    if requirements_result is not None:
        write_llm_yaml_artifact(root / "requirements_result.yaml", requirements_result)
        n += 1
    write_llm_yaml_artifact(root / "spec.yaml", spec)
    n += 1

    logger.info(
        "LLM 生出力を %s に %s ファイル保存（push に含まれます）",
        root.relative_to(site_dir),
        n,
    )
    return n


def write_manus_only_style_run_artifacts(
    site_dir: Path,
    *,
    spec: dict[str, Any],
    work_branch: ContractWorkBranch,
    partner_name: str,
    record_number: str,
) -> Path | None:
    """
    本番パイプライン: ``scripts/pipeline_test_manus_only.py`` と同じファイル構成で 1 ラン分を残す。

    - ``llm_raw_output/manus_only_tests/<UTC>/01_refactored_markdown.md``
    - ``…/02_summary.json`` / ``03_deploy_github_url.txt`` / ``00_source.json`` / ``README.txt``

    Manus リファクタが spec に載っていない（空 MD かつ deploy URL なし）ときは何も作成しない。

    引数: site_dir（generate_site 済み） / spec・work_branch（フェーズ2 出力） / 案件メタ。
    処理: プラン別の refactored・canvas キーを解決し、タイムスタンプ 1 フォルダに JSON・テキストを書く。
    出力: 作成したラン用ディレクトリ（相対パス追跡用）。未作成時は None。
    """
    pair = _MANUS_BRANCH_KEYS.get(work_branch)
    if not pair:
        return None
    refactor_key, canvas_key = pair
    raw_md = spec.get(refactor_key)
    md_body = raw_md if isinstance(raw_md, str) else ""
    md_for_trigger = md_body.strip()
    raw_url = spec.get("manus_deploy_github_url")
    url_str = raw_url.strip() if isinstance(raw_url, str) else ""
    if not md_for_trigger and not url_str:
        return None

    site_dir = site_dir.resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = site_dir / _RAW_OUTPUT_DIR / _MANUS_ONLY_TESTS_SUBDIR / stamp
    out.mkdir(parents=True, exist_ok=True)

    canvas_ref = (spec.get(canvas_key) if isinstance(spec.get(canvas_key), str) else "") or ""
    (out / "00_source.json").write_text(
        json.dumps(
            {
                "mode": "production",
                "partner_name": (partner_name or "").strip() or None,
                "record_number": (record_number or "").strip() or None,
                "work_branch": work_branch.value,
                "canvas_spec_key": canvas_key,
                "refactored_spec_key": refactor_key,
                "canvas_chars": len(canvas_ref),
                "phase1_dir": None,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (out / "01_refactored_markdown.md").write_text(
        md_body.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8"
    )
    (out / "03_deploy_github_url.txt").write_text(
        url_str + ("\n" if url_str else ""),
        encoding="utf-8",
    )
    summary = {
        "out_dir": str(out),
        "markdown_chars": len(md_body),
        "deploy_github_url": url_str or None,
        "manus_provide_url_expected": bool(url_str),
        "work_branch": work_branch.value,
    }
    (out / "02_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "README.txt").write_text(
        "\n".join(
            [
                "本番: Manus リファクタ出力（工程テスト manus_only_tests と同形式）",
                "",
                f"サイト: {site_dir.name}",
                f"03_deploy_github_url.txt: {url_str or '（空）'}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    logger.info(
        "Manus 工程テスト互換: %s に保存（markdown_chars=%s url=%s）",
        out.relative_to(site_dir),
        len(md_body),
        "yes" if url_str else "no",
    )
    return out
