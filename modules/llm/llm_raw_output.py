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

from config.config import OUTPUT_DIR
from modules.contract_workflow import ContractWorkBranch

from .llm_text_artifacts import write_llm_yaml_artifact

logger = logging.getLogger(__name__)

_RAW_OUTPUT_DIR = "llm_raw_output"
_GEMINI_STEPS_SUBDIR = "gemini_steps"
# Manus 待ちでフェーズ3に進めないときも Gemini 完了分を失わない（generate_site は sites 直下を消すため sites 外に置く）
_PHASE2_LLM_CHECKPOINT_SUBDIR = "phase2_llm_checkpoints"
# TEXT_LLM 直後・generate_site 前（フェーズ3未到達でも正本を残す）
_PHASE2_COMPLETE_SUBDIR = "phase2_complete"

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


def _site_name_for_output_path(site_name: str) -> str:
    """
    ``main`` の ``site_name``（パートナー名-レコード）と同じ見え方でパスに使う。

    ``_safe_segment`` は非 ASCII をすべて `_` にするため、日本語社名のチェックポイントが
    判別不能になる。ここではファイルシステム上危険な文字のみ置換する。
    """
    s = (site_name or "").strip() or "unnamed"
    for ch in ("/", "\\", "\x00", ":"):
        s = s.replace(ch, "_")
    return s[:240] if len(s) > 240 else s


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(normalized, encoding="utf-8")


def write_gemini_manual_step_files(
    llm_raw_root: Path,
    *,
    meta_key: str,
    steps: dict[str, Any],
    model: Any = None,
    step_prompts: dict[str, Any] | None = None,
) -> int:
    """
    ``llm_raw_root/gemini_steps/<pipe>/`` に Gemini マニュアルの steps / step_prompts / model を書く。

    引数: llm_raw_root（通常は ``.../llm_raw_output``） / meta_key（requirements のメタキー） /
          steps（応答） / model（任意） / step_prompts（任意・API 入力）。
    処理: site 正本と同じファイル命名（``_model.txt`` / ``*.md`` / ``*_prompt.txt``）。
    出力: 書いたファイル数。
    """
    n = 0
    pipe = _safe_segment(meta_key)
    base = llm_raw_root / _GEMINI_STEPS_SUBDIR / pipe
    if isinstance(model, str) and model.strip():
        _write_text(base / "_model.txt", model.strip() + "\n")
        n += 1
    for step_name, step_body in steps.items():
        if not isinstance(step_body, str) or not step_body.strip():
            continue
        fn = _safe_segment(str(step_name)) + ".md"
        _write_text(base / fn, step_body)
        n += 1
    if isinstance(step_prompts, dict):
        for prompt_key, prompt_body in step_prompts.items():
            if not isinstance(prompt_body, str) or not prompt_body.strip():
                continue
            pfn = _safe_segment(str(prompt_key)) + "_prompt.txt"
            _write_text(base / pfn, prompt_body)
            n += 1
    return n


def write_pre_manus_llm_checkpoint(
    *,
    site_name: str,
    work_branch: ContractWorkBranch,
    manual_meta_key: str,
    model: str,
    steps: dict[str, Any],
    step_prompts: dict[str, Any],
    canvas_markdown: str,
    partner_name: str,
    record_number: str,
) -> Path:
    """
    Gemini マニュアル完了直後・Manus リファクタ開始前に、生出力を ``output/`` 配下へ保存する。

    ``main.generate_site`` は ``output/sites/<site_name>/`` を退避削除するため、
    ここでは ``output/phase2_llm_checkpoints/<site_name>/pre_manus/`` にのみ書く
    （Manus で長時間ブロックしても Gemini 分はディスクに残る）。

    引数: site_name（main と同じ ``{partner}-{record}``） / work_branch / manual_meta_key /
          model・steps・step_prompts（この時点の outs） / canvas_markdown（Manus に渡す Canvas 相当） /
          partner_name・record_number（メタ用）。
    処理: ``llm_raw_output/gemini_steps/...`` 互換ツリー + ``canvas_before_manus.md`` + JSON メタ。
    出力: チェックポイントディレクトリ（絶対パス）。
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path_site = _site_name_for_output_path(site_name)
    checkpoint_dir = (
        OUTPUT_DIR.resolve()
        / _PHASE2_LLM_CHECKPOINT_SUBDIR
        / path_site
        / "pre_manus"
    )
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    llm_raw = checkpoint_dir / _RAW_OUTPUT_DIR
    n_steps = write_gemini_manual_step_files(
        llm_raw,
        meta_key=manual_meta_key,
        steps=steps,
        model=model,
        step_prompts=step_prompts,
    )
    _write_text(checkpoint_dir / "canvas_before_manus.md", canvas_markdown or "")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "checkpoint_utc": stamp,
        "site_name": site_name,
        "work_branch": work_branch.value,
        "manual_meta_key": manual_meta_key,
        "gemini_model": model,
        "partner_name": (partner_name or "").strip() or None,
        "record_number": (record_number or "").strip() or None,
        "canvas_chars": len(canvas_markdown or ""),
        "gemini_artifact_files": n_steps,
        "note": "Manus 完了前のスナップショット。完了後は output/sites/.../llm_raw_output/ が正本。",
    }
    _write_text(
        checkpoint_dir / "00_checkpoint.json",
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text(
        checkpoint_dir / "README.txt",
        "\n".join(
            [
                "フェーズ2: Gemini マニュアル完了後・Manus リファクタ待機前のチェックポイント",
                "",
                f"案件ディレクトリ名（main 準拠）: {site_name}",
                f"作業分岐: {work_branch.value}",
                f"UTC: {stamp}",
                "",
                "- llm_raw_output/gemini_steps/ … サイト正本と同形式（応答 .md / 入力 *_prompt.txt）",
                "- canvas_before_manus.md … Manus に渡す Canvas 相当テキスト",
                "- 00_checkpoint.json … メタデータ",
                "",
                "Manus が完了し main がフェーズ3に進むと output/sites/<site_name>/llm_raw_output/ に",
                "フル正本が再度書かれます（このフォルダは generate_site で削除されません）。",
                "",
            ]
        ),
    )
    logger.info(
        "Manus 待機前チェックポイント: %s に Gemini 生出力 %s ファイル（%s・絶対パス: %s）",
        checkpoint_dir.relative_to(OUTPUT_DIR.resolve()),
        n_steps + 3,
        manual_meta_key,
        checkpoint_dir,
    )
    return checkpoint_dir


def write_llm_raw_artifacts_phase2_snapshot(
    *,
    site_name: str,
    spec: dict[str, Any],
    requirements_result: dict[str, Any] | None,
    work_branch: ContractWorkBranch,
) -> Path:
    """
    TEXT_LLM 直後・``generate_site`` より前に ``output/phase2_complete/<site>/llm_raw_output/`` へ正本を書く。

    ``generate_site`` の退避削除やフェーズ3途中のクラッシュで ``output/sites/`` が空でも、
    ここにフェーズ2の spec / requirements / gemini_steps が残る（``output/`` は .gitignore）。

    引数: main と同じ site_name / フェーズ2の spec・requirements_result / work_branch。
    処理: ``write_llm_raw_artifacts`` をサイト直下相当のディレクトリに対して1回呼ぶ。
    出力: スナップショットのベースディレクトリ（絶対パス）。
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path_site = _site_name_for_output_path(site_name)
    base = OUTPUT_DIR.resolve() / _PHASE2_COMPLETE_SUBDIR / path_site
    base.mkdir(parents=True, exist_ok=True)
    _write_text(
        base / "README.txt",
        "\n".join(
            [
                "フェーズ2（TEXT_LLM）完了直後のスナップショット（generate_site・フェンス適用の前）",
                f"案件ディレクトリ名（main 準拠）: {site_name}",
                "llm_raw_output/ の中身は output/sites/<同一名前>/llm_raw_output/ と同形式。",
                "フェーズ3が成功するとサイト側にも同内容が再度保存されます。",
                "",
            ]
        ),
    )
    n = write_llm_raw_artifacts(
        base,
        spec=spec,
        requirements_result=requirements_result,
        work_branch=work_branch,
    )
    root = base / _RAW_OUTPUT_DIR
    logger.info(
        "フェーズ2スナップショット: %s ファイル（絶対パス: %s）",
        n,
        root,
    )
    return base


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
    - ``*_manual_gemini`` メタの ``steps`` 辞書（各ステップ応答 .md）と
      任意の ``step_prompts`` 辞書（API に渡したユーザー入力テキストを ``*_prompt.txt`` で保存）
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
            sp = meta.get("step_prompts")
            n += write_gemini_manual_step_files(
                root,
                meta_key=meta_key,
                steps=steps,
                model=meta.get("model"),
                step_prompts=sp if isinstance(sp, dict) else None,
            )

    if requirements_result is not None:
        write_llm_yaml_artifact(root / "requirements_result.yaml", requirements_result)
        n += 1
    write_llm_yaml_artifact(root / "spec.yaml", spec)
    n += 1

    logger.info(
        "LLM 生出力を %s に %s ファイル保存（push に含まれるのは sites 配下のみ・絶対パス: %s）",
        root.relative_to(site_dir),
        n,
        root,
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
