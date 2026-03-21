"""LLM 出力パスの安全性"""
import pytest
from modules.llm_output_files import (
    is_safe_llm_project_path,
    parse_llm_file_blocks,
    strip_markdown_code_fence,
)


@pytest.mark.parametrize(
    "rel,expected",
    [
        ("app/page.tsx", True),
        ("components/sections/Hero.tsx", True),
        ("lib/ctaButtonClass.ts", True),
        ("../etc/passwd", False),
        ("app/../../../secret", False),
        ("/absolute", False),
        ("package.json", False),
        ("node_modules/foo", False),
    ],
)
def test_is_safe_llm_project_path(rel: str, expected: bool) -> None:
    assert is_safe_llm_project_path(rel) is expected


def test_strip_markdown_code_fence() -> None:
    raw = """```tsx
export default function Page() { return null }
```"""
    assert strip_markdown_code_fence(raw) == "export default function Page() { return null }"


def test_parse_llm_file_blocks_strips_markdown_fence() -> None:
    text = """
<<<FILE app/page.tsx>>>
```tsx
export default function Page() { return null }
```
<<<ENDFILE>>>
"""
    files = parse_llm_file_blocks(text)
    assert files["app/page.tsx"] == "export default function Page() { return null }"


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


def test_parse_llm_file_blocks_spaced_markers() -> None:
    text = """
<<<  FILE  app/page.tsx  >>>
export default function Page() { return null }
<<<  ENDFILE  >>>
"""
    files = parse_llm_file_blocks(text)
    assert files.get("app/page.tsx", "").strip().startswith("export default")


def test_parse_llm_file_blocks_xml_style() -> None:
    text = """<file path="components/Foo.tsx">
export function Foo() { return null }
</file>"""
    files = parse_llm_file_blocks(text)
    assert "components/Foo.tsx" in files


def test_parse_llm_file_blocks_fenced_with_path() -> None:
    text = """```tsx app/page.tsx
export default function Page() {
  return null
}
```"""
    files = parse_llm_file_blocks(text)
    assert "app/page.tsx" in files


def test_parse_llm_file_blocks_double_angle_markers() -> None:
    text = """
<<FILE components/X.tsx>>
export function X() { return null }
<<ENDFILE>>
"""
    files = parse_llm_file_blocks(text)
    assert "components/X.tsx" in files


def test_parse_llm_file_blocks_normalizes_templates_nextjs_prefix() -> None:
    """Cursor が templates/nextjs_template/ 付きで返す場合でも app/ に正規化して受理する"""
    text = """
<<<FILE templates/nextjs_template/app/page.tsx>>>
export default function Page() { return null }
<<<ENDFILE>>>
"""
    files = parse_llm_file_blocks(text)
    assert "app/page.tsx" in files
    assert "templates/nextjs_template/app/page.tsx" not in files
