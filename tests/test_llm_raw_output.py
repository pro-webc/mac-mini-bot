"""llm_raw_output: LLM テキストを site_dir にそのまま保存"""
from pathlib import Path

from modules.contract_workflow import ContractWorkBranch
from modules.llm_raw_output import write_llm_raw_artifacts


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
    assert n == 5
    assert (site / "llm_raw_output" / "basic_lp_manual_gemini_final.md").read_text(
        encoding="utf-8"
    ) == "canvas final body"
    assert (site / "llm_raw_output" / "site_build_prompt.txt").read_text(
        encoding="utf-8"
    ).startswith("build me")
    assert (
        site / "llm_raw_output" / "gemini_steps" / "basic_lp_manual_gemini" / "step_1_1.md"
    ).read_text(encoding="utf-8") == "hello"


def test_empty_spec_writes_nothing_except_maybe_prompt(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    n = write_llm_raw_artifacts(
        site,
        spec={},
        requirements_result=None,
        work_branch=ContractWorkBranch.BASIC_LP,
    )
    assert n == 0
