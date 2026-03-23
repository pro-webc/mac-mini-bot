"""出力保存（manus_only_tests 形式）→ URL 解決 → デプロイ呼び出し相当の結合テスト。"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.saved_manus_deploy_url import (
    normalize_github_clone_url,
    read_deploy_github_url_file,
    resolve_github_url_from_manus_output_dir,
)
from modules.vercel_client import VercelClient, github_owner_repo_from_clone_url


def test_read_deploy_github_url_file_skips_comments_and_blanks(tmp_path: Path) -> None:
    p = tmp_path / "03_deploy_github_url.txt"
    p.write_text("# コメント\n\n  https://github.com/a/b  \n", encoding="utf-8")
    assert read_deploy_github_url_file(p) == "https://github.com/a/b"


def test_normalize_github_clone_url_adds_git_suffix() -> None:
    assert normalize_github_clone_url("https://github.com/o/r") == "https://github.com/o/r.git"
    assert normalize_github_clone_url("https://github.com/o/r.git") == "https://github.com/o/r.git"


def test_resolve_prefers_03_over_markdown(tmp_path: Path) -> None:
    d = tmp_path / "run"
    d.mkdir()
    (d / "03_deploy_github_url.txt").write_text("https://github.com/from/file\n", encoding="utf-8")
    (d / "01_refactored_markdown.md").write_text(
        "BOT_DEPLOY_GITHUB_URL: https://github.com/from/md.git\n", encoding="utf-8"
    )
    assert resolve_github_url_from_manus_output_dir(d) == "https://github.com/from/file"


def test_resolve_from_01_when_03_empty(tmp_path: Path) -> None:
    d = tmp_path / "run"
    d.mkdir()
    (d / "03_deploy_github_url.txt").write_text("\n", encoding="utf-8")
    (d / "01_refactored_markdown.md").write_text(
        "```\nx\n```\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/o/r.git\n", encoding="utf-8"
    )
    assert resolve_github_url_from_manus_output_dir(d) == "https://github.com/o/r.git"


def test_resolve_from_01_infer_when_no_bot_deploy_line(tmp_path: Path) -> None:
    d = tmp_path / "run"
    d.mkdir()
    (d / "01_refactored_markdown.md").write_text(
        "push 済み https://github.com/propagate-webcreation/demo-9408-shida-yoji.git です\n",
        encoding="utf-8",
    )
    (d / "00_source.json").write_text('{"record_number": "9408"}\n', encoding="utf-8")
    assert (
        resolve_github_url_from_manus_output_dir(d, record_number="9408")
        == "https://github.com/propagate-webcreation/demo-9408-shida-yoji.git"
    )


def test_saved_output_url_then_vercel_deploy_mocked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """前回保存ディレクトリ相当から URL を解決し、本番と同じ VercelClient API を呼ぶ。"""
    d = tmp_path / "20250323T000000Z"
    d.mkdir()
    (d / "03_deploy_github_url.txt").write_text("# saved\nhttps://github.com/acme/demo-repo\n", encoding="utf-8")

    raw = resolve_github_url_from_manus_output_dir(d)
    github_url = normalize_github_clone_url(raw)
    _, project_name = github_owner_repo_from_clone_url(github_url)

    calls: list[tuple[str, str]] = []

    def fake_deploy(self: VercelClient, url: str, name: str) -> dict:
        calls.append((url, name))
        return {"url": "https://demo.example.vercel.app", "deployment_id": "dep-1"}

    monkeypatch.setattr(VercelClient, "deploy_from_github", fake_deploy)
    vc = VercelClient()
    deployment = vc.deploy_from_github(github_url, project_name)

    assert deployment.get("deployment_id") == "dep-1"
    assert calls == [("https://github.com/acme/demo-repo.git", "demo-repo")]
