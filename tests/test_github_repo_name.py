"""GitHub リポジトリ名サニタイズ・clone URL パース"""
import pytest
from modules.github_client import sanitize_github_repo_name
from modules.vercel_client import github_owner_repo_from_clone_url


def test_sanitize_github_repo_name_record_ascii() -> None:
    assert sanitize_github_repo_name("株式会社TS-hub", "16715") == "16715-TS-hub"
    assert sanitize_github_repo_name("CREST", "16245") == "16245-CREST"


def test_sanitize_github_repo_name_romanize_japanese() -> None:
    name = sanitize_github_repo_name("株式会社グレードテック", "16218")
    assert name.startswith("16218-")
    assert "gureedotekku" in name.lower()

    name2 = sanitize_github_repo_name("テスト商事", "42")
    assert name2.startswith("42-")
    assert len(name2) > 3

    name3 = sanitize_github_repo_name("志田洋二", "9408")
    assert name3.startswith("9408-")
    assert len(name3) > 5


def test_sanitize_github_repo_name_strips_invalid_chars() -> None:
    assert sanitize_github_repo_name("A/B:C", "1") == "1-A-B-C"


def test_github_owner_repo_from_clone_url_https_git_suffix() -> None:
    o, r = github_owner_repo_from_clone_url(
        "https://github.com/propagate-webcreation/9408.git"
    )
    assert o == "propagate-webcreation"
    assert r == "9408"


def test_github_owner_repo_from_clone_url_no_git_suffix() -> None:
    o, r = github_owner_repo_from_clone_url(
        "https://github.com/org/my-repo"
    )
    assert o == "org"
    assert r == "my-repo"


def test_github_owner_repo_from_clone_url_invalid() -> None:
    with pytest.raises(ValueError, match="解釈できません"):
        github_owner_repo_from_clone_url("https://example.com/only-one")
