"""Manus 最終リファクタ（HTTP モック）"""
from __future__ import annotations

from typing import Any

import config.config as cfg
import pytest


class _OkJson:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.status_code = 200
        self.text = ""
        self._payload = payload

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture(autouse=True)
def _manus_fast_poll(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cfg, "MANUS_REFACTOR_POLL_INTERVAL_SEC", 0.01)
    monkeypatch.setattr(cfg, "MANUS_REFACTOR_TIMEOUT_SEC", 5.0)


def test_run_manus_refactor_stage_polls_until_completed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        assert "API_KEY" in headers
        assert json and "prompt" in json
        captured["json"] = json
        return _OkJson({"task_id": "t-1", "task_url": "https://example/manus/t-1"})

    get_n = {"i": 0}

    def fake_get(
        url: str,
        headers: dict[str, str],
        timeout: float | None = None,
    ) -> _OkJson:
        assert "API_KEY" in headers
        get_n["i"] += 1
        if get_n["i"] < 2:
            return _OkJson({"status": "running", "output": []})
        return _OkJson(
            {
                "status": "completed",
                "output": [
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "```tsx\napp/page.tsx\nx\n```"}],
                    }
                ],
            }
        )

    monkeypatch.setattr("modules.manus_refactor.requests.post", fake_post)
    monkeypatch.setattr("modules.manus_refactor.requests.get", fake_get)

    import modules.manus_refactor as mr

    monkeypatch.setattr(
        mr,
        "MANUS_TASK_CONNECTOR_IDS",
        ["bbb0df76-66bd-4a24-ae4f-2aac4750d90b"],
    )
    out = mr.run_manus_refactor_stage(
        canvas_source_code="export default function Page() { return null }"
    )
    assert "app/page.tsx" in out
    assert get_n["i"] >= 2
    assert captured["json"].get("connectors") == [
        "bbb0df76-66bd-4a24-ae4f-2aac4750d90b"
    ]


def test_run_manus_refactor_stage_omits_connectors_when_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        captured["json"] = json
        return _OkJson({"task_id": "t-2", "task_url": "https://example/manus/t-2"})

    def fake_get(
        url: str,
        headers: dict[str, str],
        timeout: float | None = None,
    ) -> _OkJson:
        return _OkJson(
            {
                "status": "completed",
                "output": [
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "ok"}],
                    }
                ],
            }
        )

    monkeypatch.setattr("modules.manus_refactor.requests.post", fake_post)
    monkeypatch.setattr("modules.manus_refactor.requests.get", fake_get)

    import modules.manus_refactor as mr

    monkeypatch.setattr(mr, "MANUS_TASK_CONNECTOR_IDS", [])
    mr.run_manus_refactor_stage(canvas_source_code="x")
    assert "connectors" not in (captured.get("json") or {})


def test_split_manus_response_deploy_url() -> None:
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "```tsx\napp/page.tsx\nx\n```\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/o/r.git"
    )
    assert url == "https://github.com/o/r.git"
    assert "app/page.tsx" in body
    assert "BOT_DEPLOY" not in body

    b2, u2 = split_manus_response_deploy_url("```\na\n```")
    assert u2 is None
    assert b2 == "```\na\n```"
