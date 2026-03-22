"""GitHub リポジトリ名サニタイズ・clone URL パース"""
import pytest
from modules.github_client import sanitize_github_repo_name
from modules.vercel_client import github_owner_repo_from_clone_url


def test_sanitize_github_repo_name_record_test_partner() -> None:
    assert sanitize_github_repo_name("株式会社TS-hub", "16715") == "16715-test-ts-hub"
    assert sanitize_github_repo_name("ignored", "42") == "42-test-ignored"


def test_sanitize_github_repo_name_strips_non_alnum_record() -> None:
    assert sanitize_github_repo_name("", "R-99x") == "R99x-test-partner"


def test_github_owner_repo_from_clone_url_https_git_suffix() -> None:
    o, r = github_owner_repo_from_clone_url(
        "https://github.com/propagate-webcreation/demo-123-ACME.git"
    )
    assert o == "propagate-webcreation"
    assert r == "demo-123-ACME"


def test_github_owner_repo_from_clone_url_no_git_suffix() -> None:
    o, r = github_owner_repo_from_clone_url(
        "https://github.com/org/my-repo"
    )
    assert o == "org"
    assert r == "my-repo"


def test_github_owner_repo_from_clone_url_invalid() -> None:
    with pytest.raises(ValueError, match="解釈できません"):
        github_owner_repo_from_clone_url("https://example.com/only-one")
