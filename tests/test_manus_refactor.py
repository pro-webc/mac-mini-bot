"""Manus 最終リファクタ（HTTP モック）"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import config.config as cfg
import pytest

_FIXTURE_MANUS_DEPLOY = (
    Path(__file__).resolve().parent / "fixtures" / "manus_response_with_deploy_url.md"
)


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
        claude_source_code="export default function Page() { return null }"
    )
    assert "app/page.tsx" in out
    assert get_n["i"] >= 2
    assert captured["json"].get("connectors") == [
        "bbb0df76-66bd-4a24-ae4f-2aac4750d90b"
    ]
    assert captured["json"].get("interactiveMode") is False


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
    mr.run_manus_refactor_stage(claude_source_code="x")
    assert "connectors" not in (captured.get("json") or {})


def test_run_manus_refactor_stage_retries_on_initial_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")

    class _Resp:
        def __init__(self, status_code: int, payload: dict[str, Any] | None, text: str = "") -> None:
            self.status_code = status_code
            self._payload = payload or {}
            self.text = text

        def json(self) -> dict[str, Any]:
            return self._payload

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        return _OkJson({"task_id": "api-task-id", "task_url": "https://manus.im/app/slug-task"})

    get_n = {"i": 0}

    def fake_get(
        url: str,
        headers: dict[str, str],
        timeout: float | None = None,
    ) -> _Resp:
        get_n["i"] += 1
        if get_n["i"] <= 2:
            return _Resp(404, None, '{"code":5,"message":"task not found"}')
        return _Resp(
            200,
            {
                "status": "completed",
                "output": [
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "ok"}],
                    }
                ],
            },
        )

    monkeypatch.setattr("modules.manus_refactor.requests.post", fake_post)
    monkeypatch.setattr("modules.manus_refactor.requests.get", fake_get)

    import modules.manus_refactor as mr

    out = mr.run_manus_refactor_stage(claude_source_code="export default function Page() { return null }")
    assert out == "ok"
    assert get_n["i"] >= 3


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


def test_split_manus_response_deploy_url_fixture_file() -> None:
    """tests/fixtures の実ファイルで BOT_DEPLOY 行を解釈できること。"""
    from modules.manus_refactor import split_manus_response_deploy_url

    text = _FIXTURE_MANUS_DEPLOY.read_text(encoding="utf-8")
    body, url = split_manus_response_deploy_url(text)
    assert url == "https://github.com/example-org/example-repo.git"
    assert "export default function Page" in body


def test_split_manus_response_deploy_url_short_body_with_trailing_newline() -> None:
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "hello\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/a/b.git\n"
    )
    assert url == "https://github.com/a/b.git"
    assert body.strip() == "hello"


def test_split_manus_response_deploy_url_after_code_fence_block() -> None:
    """フェンスブロックのあと空行・URL 行だけの構成。"""
    from modules.manus_refactor import split_manus_response_deploy_url

    text = (
        "```\n"
        "app/x.tsx\n"
        "x\n"
        "```\n"
        "\n"
        "BOT_DEPLOY_GITHUB_URL: https://github.com/pipe/line.git\n"
    )
    body, url = split_manus_response_deploy_url(text)
    assert url == "https://github.com/pipe/line.git"
    assert "app/x.tsx" in body


def test_split_manus_response_deploy_url_markdown_link_value() -> None:
    """BOT_DEPLOY 行の値がマークダウンリンクでも https を抽出する。"""
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "ok\n\nBOT_DEPLOY_GITHUB_URL: [リポジトリ](https://github.com/o/r.git)\n"
    )
    assert url == "https://github.com/o/r.git"
    assert body.strip() == "ok"


def test_split_manus_response_deploy_url_angle_brackets() -> None:
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "x\nBOT_DEPLOY_GITHUB_URL: <https://github.com/acme/proj.git>\n"
    )
    assert url == "https://github.com/acme/proj.git"
    assert body.strip() == "x"


def test_split_manus_response_deploy_url_without_git_suffix() -> None:
    from modules.manus_refactor import split_manus_response_deploy_url

    _, url = split_manus_response_deploy_url(
        "BOT_DEPLOY_GITHUB_URL: https://github.com/o/r\n"
    )
    assert url == "https://github.com/o/r"


def test_infer_manus_github_clone_url_optional_git_suffix() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    assert (
        infer_manus_github_clone_url(
            "see https://github.com/propagate-webcreation/bot-1-acme.co.jp",
            record_number="1",
        )
        == "https://github.com/propagate-webcreation/bot-1-acme.co.jp"
    )


def test_split_manus_response_deploy_url_allows_trailing_lines_after_url() -> None:
    """BOT_DEPLOY 行の後に「タスク完了」等があっても URL を取る。"""
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "memo\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/o/r.git\n\nタスクが完了しました\n"
    )
    assert url == "https://github.com/o/r.git"
    assert "タスクが完了" not in body
    assert "BOT_DEPLOY" not in body


def test_infer_manus_github_clone_url_by_record() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    prose = "push 済み https://github.com/propagate-webcreation/demo-9408-shida-yoji.git です"
    assert (
        infer_manus_github_clone_url(prose, record_number="9408")
        == "https://github.com/propagate-webcreation/demo-9408-shida-yoji.git"
    )


def test_infer_manus_github_clone_url_by_record_bot_prefix() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    prose = "push 済み https://github.com/propagate-webcreation/bot-9408-shida-yoji.git です"
    assert (
        infer_manus_github_clone_url(prose, record_number="9408")
        == "https://github.com/propagate-webcreation/bot-9408-shida-yoji.git"
    )


def test_infer_manus_github_clone_url_by_record_botrun_prefix() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    prose = "push 済み https://github.com/propagate-webcreation/BotRun-9408.git です"
    assert (
        infer_manus_github_clone_url(prose, record_number="9408")
        == "https://github.com/propagate-webcreation/BotRun-9408.git"
    )


def test_infer_manus_github_clone_url_single_without_record() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    assert (
        infer_manus_github_clone_url("URL: https://github.com/acme/one.git", record_number="")
        == "https://github.com/acme/one.git"
    )


def test_infer_manus_github_clone_url_ambiguous_returns_none() -> None:
    from modules.manus_refactor import infer_manus_github_clone_url

    t = "https://github.com/a/x.git と https://github.com/b/y.git"
    assert infer_manus_github_clone_url(t, record_number="") is None


def test_split_manus_response_deploy_url_percent_encoded_japanese() -> None:
    """BOT_DEPLOY 行のリポジトリ名がパーセントエンコードされた日本語でも抽出できる。"""
    from modules.manus_refactor import split_manus_response_deploy_url

    body, url = split_manus_response_deploy_url(
        "ok\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/propagate-webcreation/BotRun-%E5%BF%97%E7%94%B0%E6%B4%8B%E4%BA%8C.git\n"
    )
    assert url == "https://github.com/propagate-webcreation/BotRun-%E5%BF%97%E7%94%B0%E6%B4%8B%E4%BA%8C.git"
    assert body.strip() == "ok"


def test_infer_manus_github_clone_url_percent_encoded_botrun() -> None:
    """パーセントエンコードされた BotRun- URL を botrun- プレフィックスで推定できる。"""
    from modules.manus_refactor import infer_manus_github_clone_url

    prose = "push 済み https://github.com/propagate-webcreation/BotRun-%E5%BF%97%E7%94%B0%E6%B4%8B%E4%BA%8C.git です"
    assert (
        infer_manus_github_clone_url(prose, record_number="9408")
        == "https://github.com/propagate-webcreation/BotRun-%E5%BF%97%E7%94%B0%E6%B4%8B%E4%BA%8C.git"
    )


def test_infer_manus_github_clone_url_new_naming_record_ascii() -> None:
    """新命名規則 {レコード番号}-{ASCII部分} の URL をレコード番号で推定できる。"""
    from modules.manus_refactor import infer_manus_github_clone_url

    prose = "push 済み https://github.com/propagate-webcreation/9408-CREST.git です"
    assert (
        infer_manus_github_clone_url(prose, record_number="9408")
        == "https://github.com/propagate-webcreation/9408-CREST.git"
    )


def test_extract_assistant_markdown_text_type_fallback() -> None:
    """content block の type が 'text' でもテキストを取得できる。"""
    from modules.manus_refactor import _extract_assistant_markdown

    task = {
        "status": "completed",
        "output": [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "hello world"}],
            }
        ],
    }
    assert _extract_assistant_markdown(task) == "hello world"


def test_extract_assistant_markdown_direct_text_fallback() -> None:
    """output メッセージに content が無く直接 text がある古い形式。"""
    from modules.manus_refactor import _extract_assistant_markdown

    task = {
        "status": "completed",
        "output": [
            {"role": "assistant", "text": "direct text"},
        ],
    }
    assert _extract_assistant_markdown(task) == "direct text"


def test_interactive_mode_false_sent_in_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """MANUS_INTERACTIVE_MODE=false が API リクエストボディに含まれる。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    monkeypatch.setattr(cfg, "MANUS_INTERACTIVE_MODE", False)
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        captured["json"] = json
        return _OkJson({"task_id": "t-im", "task_url": "https://example/manus/t-im"})

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
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

    mr.run_manus_refactor_stage(claude_source_code="x")
    assert captured["json"]["interactiveMode"] is False


def test_interactive_mode_true_sent_in_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """MANUS_INTERACTIVE_MODE=true のとき API ボディに True が入る。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        captured["json"] = json
        return _OkJson({"task_id": "t-im2", "task_url": "https://example/manus/t-im2"})

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
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

    monkeypatch.setattr(mr, "MANUS_INTERACTIVE_MODE", True)
    mr.run_manus_refactor_stage(claude_source_code="x")
    assert captured["json"]["interactiveMode"] is True


def test_task_body_contains_attachments_with_base64_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """attachments がタスク作成リクエストに含まれ、base64 形式であること。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        **kw: Any,
    ) -> _OkJson:
        if json and "prompt" in json:
            captured["json"] = json
        return _OkJson({"task_id": "t-att", "task_url": "https://example/manus/t-att"})

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
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

    mr.run_manus_refactor_stage(
        claude_source_code="export default function Page() { return null }",
        partner_name="テスト株式会社",
        record_number="99999",
    )
    body = captured["json"]
    assert "attachments" in body
    atts = body["attachments"]
    assert len(atts) == 2
    filenames = {a["filename"] for a in atts}
    assert "refactoring_instructions.md" in filenames
    assert "claude_source.tsx" in filenames
    for a in atts:
        assert "fileData" in a, f"{a['filename']} should use base64 fallback in test"
        assert a["fileData"].startswith("data:text/plain;base64,")


def test_task_body_attachments_with_file_upload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Files API が成功するとき file_id 形式で添付されること。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}
    upload_calls: list[str] = []

    class _PutOk:
        status_code = 200
        text = ""

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        **kw: Any,
    ) -> _OkJson:
        if json and "filename" in json and "prompt" not in json:
            return _OkJson({
                "id": f"file-{json['filename']}",
                "upload_url": f"https://s3.example/{json['filename']}",
            })
        if json and "prompt" in json:
            captured["json"] = json
        return _OkJson({"task_id": "t-fu", "task_url": "https://example/manus/t-fu"})

    def fake_put(url: str, data: Any = None, headers: Any = None, timeout: Any = None) -> _PutOk:
        upload_calls.append(url)
        return _PutOk()

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
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
    monkeypatch.setattr("modules.manus_refactor.requests.put", fake_put)
    monkeypatch.setattr("modules.manus_refactor.requests.get", fake_get)

    import modules.manus_refactor as mr

    mr.run_manus_refactor_stage(
        claude_source_code="export default function Page() { return null }",
    )
    body = captured["json"]
    atts = body["attachments"]
    assert len(atts) == 2
    assert all("file_id" in a for a in atts)
    assert atts[0]["file_id"] == "file-refactoring_instructions.md"
    assert atts[1]["file_id"] == "file-claude_source.tsx"
    assert len(upload_calls) == 2


def test_prompt_is_shorter_than_full_embed(monkeypatch: pytest.MonkeyPatch) -> None:
    """attachments 分離版の prompt はソースコード非埋め込みのため短い。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        **kw: Any,
    ) -> _OkJson:
        if json and "prompt" in json:
            captured["json"] = json
        return _OkJson({"task_id": "t-sz", "task_url": "https://example/manus/t-sz"})

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
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

    big_source = "export default function Page() { return <div>" + ("x" * 50_000) + "</div> }"

    import modules.manus_refactor as mr

    mr.run_manus_refactor_stage(claude_source_code=big_source)
    prompt_text = captured["json"]["prompt"]
    assert len(prompt_text) < 50_000, (
        f"prompt should not contain full source: {len(prompt_text)} chars"
    )
    assert "```tsx\nexport default function Page()" not in prompt_text
    assert "添付ファイル" in prompt_text


def test_build_manus_refactor_prompt_and_attachments_structure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """分離版が正しい構造を返すこと。"""
    import modules.basic_lp_refactor_claude as refactor_mod

    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", True)
    prompt, atts = refactor_mod.build_manus_refactor_prompt_and_attachments(
        "export default function Page() { return null }",
        partner_name="テスト商事",
        record_number="12345",
        contract_max_pages=6,
    )
    assert "添付ファイル" in prompt
    assert "claude_source.tsx" in prompt
    assert "refactoring_instructions.md" in prompt
    assert "```tsx\nexport default function" not in prompt
    assert "BOT_DEPLOY_GITHUB_URL:" in prompt
    assert "12345" in prompt
    assert "テスト商事" in prompt

    assert len(atts) == 2
    assert atts[0]["filename"] == "refactoring_instructions.md"
    assert atts[1]["filename"] == "claude_source.tsx"
    assert "export default function Page()" in atts[1]["content"]
    assert "契約ページ数" in atts[0]["content"]


def test_build_manus_refactor_prompt_and_attachments_no_deploy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MANUS_PROVIDES_DEPLOY_GITHUB_URL=false で deploy ブロックが省かれること。"""
    import modules.basic_lp_refactor_claude as refactor_mod

    monkeypatch.setattr(refactor_mod, "MANUS_PROVIDES_DEPLOY_GITHUB_URL", False)
    prompt, atts = refactor_mod.build_manus_refactor_prompt_and_attachments(
        "export default function Page() { return null }",
    )
    assert "BOT_DEPLOY_GITHUB_URL:" not in prompt
    assert len(atts) == 2


def test_pending_hang_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    """interactiveMode=false かつ pending が閾値を超えると早期打ち切り。"""
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "test-key")
    monkeypatch.setattr(cfg, "MANUS_INTERACTIVE_MODE", False)
    monkeypatch.setattr(cfg, "MANUS_REFACTOR_POLL_INTERVAL_SEC", 0.001)
    monkeypatch.setattr(cfg, "MANUS_REFACTOR_TIMEOUT_SEC", 60.0)

    def fake_post(
        url: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _OkJson:
        return _OkJson({"task_id": "t-hang", "task_url": "https://example/manus/t-hang"})

    call_count = {"i": 0}

    def fake_get(
        url: str, headers: dict[str, str], timeout: float | None = None
    ) -> _OkJson:
        call_count["i"] += 1
        if call_count["i"] == 1:
            return _OkJson({"status": "running", "output": []})
        return _OkJson({"status": "pending", "output": []})

    monkeypatch.setattr("modules.manus_refactor.requests.post", fake_post)
    monkeypatch.setattr("modules.manus_refactor.requests.get", fake_get)

    import modules.manus_refactor as mr

    monkeypatch.setattr(mr, "_PENDING_HANG_THRESHOLD", 0.01)
    with pytest.raises(RuntimeError, match="pending のまま"):
        mr.run_manus_refactor_stage(claude_source_code="x")
