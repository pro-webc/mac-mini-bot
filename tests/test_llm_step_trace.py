"""llm_step_trace: 案件フォルダとステップ入出力の保存"""
from __future__ import annotations

from modules.llm import llm_step_trace as t


def test_sanitize_record_folder(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("config.config.OUTPUT_DIR", tmp_path)
    root = t.ensure_case_trace_dir("14732")
    assert root == (tmp_path / "14732").resolve()
    assert (root / "llm_steps").is_dir()


def test_record_llm_turn_writes_when_active(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("config.config.OUTPUT_DIR", tmp_path)
    root = t.begin_case_llm_trace("99")
    try:
        t.record_llm_turn(
            kind="claude_cli_generate",
            input_text="hello",
            output_text="world",
        )
        step = root / "llm_steps" / "001_claude_cli_generate"
        assert (step / "input.md").read_text(encoding="utf-8") == "hello"
        assert (step / "output.md").read_text(encoding="utf-8") == "world"
    finally:
        t.end_case_llm_trace()


def test_record_llm_turn_noop_without_begin(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("config.config.OUTPUT_DIR", tmp_path)
    t.end_case_llm_trace()
    t.record_llm_turn(kind="x", input_text="a", output_text="b")
    assert not (tmp_path / "llm_steps").exists()


def test_sanitize_empty_record_is_no_record(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("config.config.OUTPUT_DIR", tmp_path)
    root = t.ensure_case_trace_dir("")
    assert root.name == "no_record"
