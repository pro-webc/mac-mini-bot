"""GitHub リポジトリ名サニタイズ"""
from modules.github_client import sanitize_github_repo_name


def test_sanitize_github_repo_name_test_prefix() -> None:
    assert sanitize_github_repo_name("株式会社TS-hub", "16715") == "test-16715"
    assert sanitize_github_repo_name("ignored", "42") == "test-42"


def test_sanitize_github_repo_name_strips_non_alnum_record() -> None:
    # ハイフン等は除去し、残った英数字を連結
    assert sanitize_github_repo_name("", "R-99x") == "test-R99x"
