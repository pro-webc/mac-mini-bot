"""Vercel プロジェクト名サニタイズ（Manus 由来の GitHub リポ名対策）"""

from modules.vercel_client import sanitize_vercel_project_name


def test_lowercase_and_double_hyphen_collapsed() -> None:
    assert sanitize_vercel_project_name("demo-16715--TS-hub") == "demo-16715-ts-hub"


def test_triple_hyphen_removed() -> None:
    assert "---" not in sanitize_vercel_project_name("my---repo")
    assert sanitize_vercel_project_name("my---repo") == "my-repo"


def test_invalid_chars_to_hyphen() -> None:
    assert sanitize_vercel_project_name("foo bar/baz") == "foo-bar-baz"


def test_empty_fallback() -> None:
    assert sanitize_vercel_project_name("") == "project"
    assert sanitize_vercel_project_name("   ") == "project"


def test_max_length() -> None:
    long_name = "a" * 120
    out = sanitize_vercel_project_name(long_name)
    assert len(out) <= 100
