"""llm_raw_output: LLM テキストを site_dir にそのまま保存"""
import json
from pathlib import Path

from modules.contract_workflow import ContractWorkBranch
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_llm_raw_artifacts_phase2_snapshot,
    write_manus_only_style_run_artifacts,
    write_pre_manus_llm_checkpoint,
)


def test_write_pre_manus_checkpoint_under_output_dir(
    tmp_path: Path, monkeypatch: object
) -> None:
    """Manus 待機前チェックポイントは OUTPUT_DIR 配下（sites の削除で消えない）。"""
    monkeypatch.setattr("modules.llm.llm_raw_output.OUTPUT_DIR", tmp_path)
    out = write_pre_manus_llm_checkpoint(
        site_name="Acme-42",
        work_branch=ContractWorkBranch.STANDARD,
        manual_meta_key="standard_cp_manual_claude",
        model="claude-opus-4-6",
        steps={"step_1_1": "resp"},
        step_prompts={"step_1_1": "ask"},
        canvas_markdown="# canvas",
        partner_name="Acme",
        record_number="42",
    )
    assert out.is_dir()
    assert out.name == "pre_manus"
    gem = (
        out
        / "llm_raw_output"
        / "claude_steps"
        / "standard_cp_manual_claude"
        / "step_1_1.md"
    )
    assert gem.read_text(encoding="utf-8") == "resp"
    assert (
        out
        / "llm_raw_output"
        / "claude_steps"
        / "standard_cp_manual_claude"
        / "step_1_1_prompt.txt"
    ).read_text(encoding="utf-8") == "ask"
    assert (out / "canvas_before_manus.md").read_text(encoding="utf-8") == "# canvas"
    meta = json.loads((out / "00_checkpoint.json").read_text(encoding="utf-8"))
    assert meta["work_branch"] == "standard"
    assert meta["manual_meta_key"] == "standard_cp_manual_claude"


def test_phase2_complete_snapshot_writes_llm_raw(
    tmp_path: Path, monkeypatch: object
) -> None:
    monkeypatch.setattr("modules.llm.llm_raw_output.OUTPUT_DIR", tmp_path)
    base = write_llm_raw_artifacts_phase2_snapshot(
        site_name="Co-1",
        spec={"basic_lp_manual_claude_final": "c"},
        requirements_result={
            "basic_lp_manual_claude": {
                "model": "m",
                "steps": {"s": "t"},
            }
        },
        work_branch=ContractWorkBranch.BASIC_LP,
    )
    assert (base / "README.txt").is_file()
    assert (base / "llm_raw_output" / "spec.yaml").is_file()
    assert (base / "llm_raw_output" / "claude_steps" / "basic_lp_manual_claude" / "s.md").read_text(
        encoding="utf-8"
    ) == "t"


def test_pre_manus_checkpoint_keeps_unicode_site_folder(
    tmp_path: Path, monkeypatch: object
) -> None:
    """チェックポイント親フォルダ名は main の site_name と同様に非 ASCII を潰さない。"""
    monkeypatch.setattr("modules.llm.llm_raw_output.OUTPUT_DIR", tmp_path)
    write_pre_manus_llm_checkpoint(
        site_name="株式会社アンカートレーディング-16308",
        work_branch=ContractWorkBranch.STANDARD,
        manual_meta_key="standard_cp_manual_claude",
        model="m",
        steps={"a": "b"},
        step_prompts={},
        canvas_markdown="",
        partner_name="株式会社アンカートレーディング",
        record_number="16308",
    )
    assert (
        tmp_path / "phase2_llm_checkpoints" / "株式会社アンカートレーディング-16308" / "pre_manus"
    ).is_dir()


def test_write_spec_and_steps(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    spec = {
        "basic_lp_refactored_source_markdown": "```tsx\napp/page.tsx\nx\n```",
        "basic_lp_manual_claude_final": "canvas final body",
    }
    req = {
        "site_build_prompt": "build me a site",
        "basic_lp_manual_claude": {
            "model": "claude-test",
            "steps": {"step_1_1": "hello", "step_empty": ""},
            "step_prompts": {"step_1_1": "prompt text for step 1-1"},
        },
    }
    n = write_llm_raw_artifacts(
        site,
        spec=spec,
        requirements_result=req,
        work_branch=ContractWorkBranch.BASIC_LP,
    )
    assert n == 8
    assert (site / "llm_raw_output" / "basic_lp_manual_claude_final.md").read_text(
        encoding="utf-8"
    ) == "canvas final body"
    assert (site / "llm_raw_output" / "site_build_prompt.txt").read_text(
        encoding="utf-8"
    ).startswith("build me")
    assert (
        site / "llm_raw_output" / "claude_steps" / "basic_lp_manual_claude" / "step_1_1.md"
    ).read_text(encoding="utf-8") == "hello"
    assert (
        site
        / "llm_raw_output"
        / "claude_steps"
        / "basic_lp_manual_claude"
        / "step_1_1_prompt.txt"
    ).read_text(encoding="utf-8") == "prompt text for step 1-1"
    assert (site / "llm_raw_output" / "requirements_result.yaml").is_file()
    assert (site / "llm_raw_output" / "spec.yaml").is_file()


def test_manus_deploy_github_url_saved_as_txt_not_md(tmp_path: Path) -> None:
    """単一 URL は Markdown 扱いにしない（プレビューでリンク下線にならない）。"""
    site = tmp_path / "site"
    site.mkdir()
    url = "https://github.com/o/r.git"
    n = write_llm_raw_artifacts(
        site,
        spec={"manus_deploy_github_url": url},
        requirements_result=None,
        work_branch=ContractWorkBranch.STANDARD,
    )
    assert n == 2  # spec.yaml + deploy url
    p = site / "llm_raw_output" / "manus_deploy_github_url.txt"
    assert p.is_file()
    assert p.read_text(encoding="utf-8").strip() == url
    assert not (site / "llm_raw_output" / "manus_deploy_github_url.md").exists()


def test_empty_spec_writes_spec_yaml_only(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    n = write_llm_raw_artifacts(
        site,
        spec={},
        requirements_result=None,
        work_branch=ContractWorkBranch.BASIC_LP,
    )
    assert n == 1
    assert (site / "llm_raw_output" / "spec.yaml").read_text(encoding="utf-8").strip() == "{}"


def test_manus_only_style_skips_when_no_manus_output(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    out = write_manus_only_style_run_artifacts(
        site,
        spec={"basic_lp_refactored_source_markdown": "  \n"},
        work_branch=ContractWorkBranch.BASIC_LP,
        partner_name="P",
        record_number="1",
    )
    assert out is None
    assert not (site / "llm_raw_output" / "manus_only_tests").is_dir()


def test_manus_only_style_writes_test_like_layout(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    created = write_manus_only_style_run_artifacts(
        site,
        spec={
            "basic_lp_refactored_source_markdown": "# fenced\n",
            "basic_lp_manual_claude_final": "canvas",
            "manus_deploy_github_url": "https://github.com/o/r.git",
        },
        work_branch=ContractWorkBranch.BASIC_LP,
        partner_name="Acme",
        record_number="42",
    )
    assert created is not None
    assert created.parent.name == "manus_only_tests"
    assert (created / "01_refactored_markdown.md").read_text(encoding="utf-8") == "# fenced\n"
    assert (created / "03_deploy_github_url.txt").read_text(
        encoding="utf-8"
    ) == "https://github.com/o/r.git\n"
    src = json.loads((created / "00_source.json").read_text(encoding="utf-8"))
    assert src["mode"] == "production"
    assert src["partner_name"] == "Acme"
    assert src["record_number"] == "42"
    assert src["work_branch"] == "basic_lp"
