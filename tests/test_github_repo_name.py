"""GitHub リポジトリ名サニタイズ"""
from modules.github_client import sanitize_github_repo_name


def test_sanitize_github_repo_name_record_test_partner() -> None:
    assert sanitize_github_repo_name("株式会社TS-hub", "16715") == "16715-test-ts-hub"
    assert sanitize_github_repo_name("ignored", "42") == "42-test-ignored"


def test_sanitize_github_repo_name_strips_non_alnum_record() -> None:
    assert sanitize_github_repo_name("", "R-99x") == "R99x-test-partner"
