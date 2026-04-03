"""modules.correction_flow のテスト"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.correction_flow import (
    _build_correction_prompt,
    _build_investigation_prompt,
    _format_slack_messages_for_prompt,
    _read_llm_trace_summary,
    _save_correction_log,
)
from modules.slack_client import CorrectionMessage


# ---------------------------------------------------------------------------
# _format_slack_messages_for_prompt
# ---------------------------------------------------------------------------


class TestFormatSlackMessages:
    def test_formats_parent_and_reply(self) -> None:
        msgs = [
            CorrectionMessage(text="#12345 色を修正", ts="1000", user="U1", is_reply=False),
            CorrectionMessage(text="青にしてください", ts="1001", user="U2", is_reply=True),
        ]
        result = _format_slack_messages_for_prompt(msgs)
        assert "投稿: #12345 色を修正" in result
        assert "リプライ: 青にしてください" in result

    def test_empty_list(self) -> None:
        assert _format_slack_messages_for_prompt([]) == ""


# ---------------------------------------------------------------------------
# _read_llm_trace_summary
# ---------------------------------------------------------------------------


class TestReadLlmTraceSummary:
    def test_returns_no_trace_when_dir_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import config.config as cfg
        monkeypatch.setattr(cfg, "OUTPUT_DIR", Path("/nonexistent"))
        # Re-import to pick up monkeypatched value
        from modules import correction_flow
        monkeypatch.setattr(correction_flow, "OUTPUT_DIR", Path("/nonexistent"))
        result = _read_llm_trace_summary("99999")
        assert "トレースなし" in result

    def test_reads_existing_trace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import correction_flow
        monkeypatch.setattr(correction_flow, "OUTPUT_DIR", tmp_path)

        trace_dir = tmp_path / "12345" / "llm_steps" / "001_claude_cli_generate"
        trace_dir.mkdir(parents=True)
        (trace_dir / "input.md").write_text("テスト入力")
        (trace_dir / "output.md").write_text("テスト出力")

        result = _read_llm_trace_summary("12345")
        assert "001_claude_cli_generate" in result
        assert "テスト入力" in result
        assert "テスト出力" in result


# ---------------------------------------------------------------------------
# _save_correction_log
# ---------------------------------------------------------------------------


class TestSaveCorrectionLog:
    def test_saves_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from modules import correction_flow
        monkeypatch.setattr(correction_flow, "OUTPUT_DIR", tmp_path)

        msgs = [CorrectionMessage(text="色修正", ts="1000", user="U1", is_reply=False)]
        investigation = {
            "root_cause": {"step": "004", "issue": "色未反映", "category": "color_mismatch"},
            "improvement_suggestion": {"target_file": "step_04.txt", "description": "色指定を明記"},
        }

        log_path = _save_correction_log("12345", "テスト社", msgs, investigation, "色を変更しました")

        assert log_path.exists()
        data = json.loads(log_path.read_text())
        assert data["record_number"] == "12345"
        assert data["root_cause"]["category"] == "color_mismatch"
        assert "色修正" in data["slack_messages"]


# ---------------------------------------------------------------------------
# プロンプト生成
# ---------------------------------------------------------------------------


class TestPrompts:
    def test_investigation_prompt_contains_record(self) -> None:
        prompt = _build_investigation_prompt("色修正", "trace", "テスト社", "12345")
        assert "12345" in prompt
        assert "テスト社" in prompt
        assert "色修正" in prompt

    def test_correction_prompt_contains_instructions(self) -> None:
        prompt = _build_correction_prompt("電話番号を追加", "テスト社")
        assert "電話番号を追加" in prompt
        assert "テスト社" in prompt
        assert "Tailwind" in prompt
