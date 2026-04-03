"""modules.self_improvement のテスト"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.self_improvement import (
    PIPELINE_MANIFEST,
    _apply_edit_to_prompt,
    _build_deep_investigation_prompt,
    _extract_step_number,
    detect_plan_type,
    list_trace_steps,
    read_all_traces_summary,
    read_full_trace,
    resolve_prompt_files,
)


# ---------------------------------------------------------------------------
# パイプラインマニフェストの整合性
# ---------------------------------------------------------------------------


class TestPipelineManifest:
    def test_all_plan_types_present(self) -> None:
        assert "basic_lp" in PIPELINE_MANIFEST
        assert "basic" in PIPELINE_MANIFEST
        assert "standard" in PIPELINE_MANIFEST
        assert "advance" in PIPELINE_MANIFEST

    def test_basic_lp_has_code_gen_steps(self) -> None:
        steps = PIPELINE_MANIFEST["basic_lp"]
        # step_8_1, 8_2, 8_3 はコード生成ステップ
        assert 12 in steps  # step_8_1
        assert 13 in steps  # step_8_2
        assert 14 in steps  # step_8_3

    def test_all_prompt_files_exist(self) -> None:
        """マニフェストで参照されるプロンプトファイルが実在するか確認。"""
        prompts_dir = Path(__file__).resolve().parent.parent / "config" / "prompts"
        missing: list[str] = []
        for plan_type, steps in PIPELINE_MANIFEST.items():
            for step_num, files in steps.items():
                for f in files:
                    if not (prompts_dir / f).is_file():
                        missing.append(f"{plan_type}[{step_num}]: {f}")
        assert not missing, f"存在しないプロンプトファイル: {missing}"


# ---------------------------------------------------------------------------
# _extract_step_number
# ---------------------------------------------------------------------------


class TestExtractStepNumber:
    def test_normal(self) -> None:
        assert _extract_step_number("009_claude_cli_chat") == 9

    def test_three_digits(self) -> None:
        assert _extract_step_number("014_claude_cli_chat") == 14

    def test_manus(self) -> None:
        assert _extract_step_number("013_manus_refactor") == 13

    def test_invalid(self) -> None:
        assert _extract_step_number("no_number") is None


# ---------------------------------------------------------------------------
# detect_plan_type
# ---------------------------------------------------------------------------


class TestDetectPlanType:
    def test_reads_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)

        yaml_dir = tmp_path / "12345" / "llm_raw_output"
        yaml_dir.mkdir(parents=True)
        (yaml_dir / "requirements_result.yaml").write_text("plan_type: basic_lp\nother: value\n")

        assert detect_plan_type("12345") == "basic_lp"

    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)

        assert detect_plan_type("99999") is None

    def test_no_plan_type_field(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)

        yaml_dir = tmp_path / "12345" / "llm_raw_output"
        yaml_dir.mkdir(parents=True)
        (yaml_dir / "requirements_result.yaml").write_text("other: value\n")

        assert detect_plan_type("12345") is None


# ---------------------------------------------------------------------------
# read_full_trace / list_trace_steps
# ---------------------------------------------------------------------------


class TestTraceReading:
    def _setup_trace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)

        step_dir = tmp_path / "12345" / "llm_steps" / "009_claude_cli_chat"
        step_dir.mkdir(parents=True)
        (step_dir / "input.md").write_text("full prompt text here")
        (step_dir / "output.md").write_text("full output text here")

        step_dir2 = tmp_path / "12345" / "llm_steps" / "010_claude_cli_chat"
        step_dir2.mkdir(parents=True)
        (step_dir2 / "input.md").write_text("next step prompt")
        (step_dir2 / "error.txt").write_text("error occurred")

        return tmp_path

    def test_read_full_trace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self._setup_trace(tmp_path, monkeypatch)
        trace = read_full_trace("12345", "009_claude_cli_chat")
        assert trace["input"] == "full prompt text here"
        assert trace["output"] == "full output text here"
        assert trace["error"] == ""

    def test_read_error_trace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self._setup_trace(tmp_path, monkeypatch)
        trace = read_full_trace("12345", "010_claude_cli_chat")
        assert trace["error"] == "error occurred"

    def test_list_steps(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self._setup_trace(tmp_path, monkeypatch)
        steps = list_trace_steps("12345")
        assert steps == ["009_claude_cli_chat", "010_claude_cli_chat"]

    def test_missing_record(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)
        assert list_trace_steps("99999") == []
        trace = read_full_trace("99999", "001_x")
        assert trace == {"input": "", "output": "", "error": ""}


# ---------------------------------------------------------------------------
# resolve_prompt_files
# ---------------------------------------------------------------------------


class TestResolvePromptFiles:
    def test_basic_lp_step_5(self) -> None:
        files = resolve_prompt_files("basic_lp", "009_claude_cli_chat")
        assert len(files) >= 1
        assert any("step_5.txt" in str(f) for f in files)

    def test_basic_lp_step_8_3(self) -> None:
        files = resolve_prompt_files("basic_lp", "014_claude_cli_chat")
        assert any("step_8_3.txt" in str(f) for f in files)

    def test_unknown_plan_generate(self) -> None:
        files = resolve_prompt_files("nonexistent", "001_claude_cli_generate")
        # claude_cli_generate はマニフェスト未登録でも URL抽出にフォールバック
        assert all("extract_reference_urls" in str(f) for f in files)

    def test_manus_step(self) -> None:
        files = resolve_prompt_files("basic_lp", "013_manus_refactor")
        assert len(files) >= 1


# ---------------------------------------------------------------------------
# _apply_edit_to_prompt
# ---------------------------------------------------------------------------


class TestApplyEditToPrompt:
    def test_replace_existing(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("before\nold rule\nafter")
        result = _apply_edit_to_prompt(f, "old rule", "new rule", "")
        assert result is True
        content = f.read_text()
        assert "new rule" in content
        assert "old rule" not in content

    def test_insert_after(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("before\ninsertion_point\nafter")
        result = _apply_edit_to_prompt(f, "", "added rule", "insertion_point")
        assert result is True
        content = f.read_text()
        assert "insertion_point\nadded rule" in content

    def test_append_fallback(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("existing content")
        result = _apply_edit_to_prompt(f, "", "new rule", "")
        assert result is True
        content = f.read_text()
        assert "new rule" in content
        assert content.startswith("existing content")

    def test_no_match(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("existing content")
        result = _apply_edit_to_prompt(f, "nonexistent text", "replacement", "")
        assert result is False

    def test_missing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "missing.txt"
        result = _apply_edit_to_prompt(f, "", "added", "")
        assert result is False


# ---------------------------------------------------------------------------
# _build_deep_investigation_prompt
# ---------------------------------------------------------------------------


class TestBuildDeepInvestigationPrompt:
    def test_contains_all_context(self) -> None:
        prompt = _build_deep_investigation_prompt(
            slack_text="#12345 color mismatch",
            step_name="009_claude_cli_chat",
            full_trace={"input": "full prompt", "output": "full output", "error": ""},
            prompt_contents={"config/prompts/basic_lp_manual/step_5.txt": "template content"},
            all_steps_summary="steps summary",
            record_number="12345",
            partner_name="TestCorp",
        )
        assert "12345" in prompt
        assert "TestCorp" in prompt
        assert "color mismatch" in prompt
        assert "full prompt" in prompt
        assert "full output" in prompt
        assert "template content" in prompt
        assert "step_5.txt" in prompt
        assert "root_cause" in prompt
        assert "improvement" in prompt


# ---------------------------------------------------------------------------
# read_all_traces_summary
# ---------------------------------------------------------------------------


class TestReadAllTracesSummary:
    def test_summary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)

        step_dir = tmp_path / "12345" / "llm_steps" / "001_claude_cli_generate"
        step_dir.mkdir(parents=True)
        (step_dir / "input.md").write_text("input test")
        (step_dir / "output.md").write_text("output test")

        summary = read_all_traces_summary("12345", max_chars=100)
        assert "001_claude_cli_generate" in summary
        assert "input test" in summary
        assert "output test" in summary
        assert "[ok]" in summary

    def test_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import self_improvement
        monkeypatch.setattr(self_improvement, "OUTPUT_DIR", tmp_path)
        assert "トレースなし" in read_all_traces_summary("99999")
