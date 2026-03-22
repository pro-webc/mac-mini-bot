"""llm_raw_output: LLM テキストを site_dir にそのまま保存"""
import json
from pathlib import Path

from modules.contract_workflow import ContractWorkBranch
from modules.llm.llm_raw_output import (
    write_llm_raw_artifacts,
    write_manus_only_style_run_artifacts,
)


def test_write_spec_and_steps(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    spec = {
        "basic_lp_refactored_source_markdown": "```tsx\napp/page.tsx\nx\n```",
        "basic_lp_manual_gemini_final": "canvas final body",
    }
    req = {
        "site_build_prompt": "build me a site",
        "basic_lp_manual_gemini": {
            "model": "gemini-test",
            "steps": {"step_1_1": "hello", "step_empty": ""},
        },
    }
    n = write_llm_raw_artifacts(
        site,
        spec=spec,
        requirements_result=req,
        work_branch=ContractWorkBranch.BASIC_LP,
    )
    assert n == 7
    assert (site / "llm_raw_output" / "basic_lp_manual_gemini_final.md").read_text(
        encoding="utf-8"
    ) == "canvas final body"
    assert (site / "llm_raw_output" / "site_build_prompt.txt").read_text(
        encoding="utf-8"
    ).startswith("build me")
    assert (
        site / "llm_raw_output" / "gemini_steps" / "basic_lp_manual_gemini" / "step_1_1.md"
    ).read_text(encoding="utf-8") == "hello"
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
            "basic_lp_manual_gemini_final": "canvas",
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
