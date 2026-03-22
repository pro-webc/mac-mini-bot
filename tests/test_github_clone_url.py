"""authenticated_https_clone_url の単体テスト"""

from __future__ import annotations

from modules.github_client import authenticated_https_clone_url


def test_authenticated_https_clone_url_inserts_token() -> None:
    out = authenticated_https_clone_url(
        "https://github.com/foo/bar",
        github_token="secret",
    )
    assert out == "https://x-access-token:secret@github.com/foo/bar.git"


def test_authenticated_https_clone_url_non_github_unchanged() -> None:
    out = authenticated_https_clone_url(
        "https://example.com/x.git",
        github_token="secret",
    )
    assert out == "https://example.com/x.git"


def test_authenticated_https_clone_url_empty_token() -> None:
    out = authenticated_https_clone_url(
        "https://github.com/org/repo.git",
        github_token="",
    )
    assert out == "https://github.com/org/repo.git"
