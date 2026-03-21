"""LLM 出力パスの安全性"""
import pytest
from modules.llm_output_files import is_safe_llm_project_path, parse_llm_file_blocks


@pytest.mark.parametrize(
    "rel,expected",
    [
        ("app/page.tsx", True),
        ("components/sections/Hero.tsx", True),
        ("../etc/passwd", False),
        ("app/../../../secret", False),
        ("/absolute", False),
        ("package.json", False),
        ("node_modules/foo", False),
    ],
)
def test_is_safe_llm_project_path(rel: str, expected: bool) -> None:
    assert is_safe_llm_project_path(rel) is expected


def test_parse_llm_file_blocks_filters_unsafe() -> None:
    text = """
<<<FILE app/page.tsx>>>
export default function Page() { return null }
<<<ENDFILE>>>
<<<FILE ../../evil.ts>>>
hack
<<<ENDFILE>>>
"""
    files = parse_llm_file_blocks(text)
    assert "app/page.tsx" in files
    assert "../../evil.ts" not in files
