"""BASIC LP 生成マークダウン → ファイル適用"""
from pathlib import Path

from modules.basic_lp_generated_apply import (
    apply_basic_lp_generated_markdown,
    collect_generated_files_from_markdown,
)


def test_parse_two_files() -> None:
    md = """
前置テキスト
```tsx
app/page.tsx
import { X } from "./x";
export default function P() { return <X />; }
```
```tsx
app/components/home/Hero.tsx
export function Hero() { return <div />; }
```
"""
    m = collect_generated_files_from_markdown(md)
    assert set(m.keys()) == {"app/page.tsx", "app/components/home/Hero.tsx"}
    assert "export default function P" in m["app/page.tsx"]


def test_parse_opener_path_only() -> None:
    md = """```app/globals.css
:root { --x: 1; }
```"""
    m = collect_generated_files_from_markdown(md)
    assert "app/globals.css" in m


def test_parse_src_app_alias() -> None:
    md = """```tsx
src/app/page.tsx
export default function Page() { return null; }
```"""
    m = collect_generated_files_from_markdown(md)
    assert "app/page.tsx" in m


def test_parse_file_prefix_and_leading_blanks() -> None:
    md = """```tsx

File: app/layout.tsx
export default function RootLayout() { return null; }
```"""
    m = collect_generated_files_from_markdown(md)
    assert "app/layout.tsx" in m


def test_parse_backtick_wrapped_path() -> None:
    md = """```tsx
`app/page.tsx`
export default function Page() { return null; }
```"""
    m = collect_generated_files_from_markdown(md)
    assert "app/page.tsx" in m


def test_apply_writes_files(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    md = """```tsx
app/page.tsx
export default function Page() { return null; }
```"""
    n = apply_basic_lp_generated_markdown(site_dir=site, markdown=md)
    assert n == 1
    assert (site / "app" / "page.tsx").read_text(encoding="utf-8").strip().startswith(
        "export default"
    )


def test_apply_rejects_escape(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    md = """```tsx
../evil.txt
x
```"""
    n = apply_basic_lp_generated_markdown(site_dir=site, markdown=md)
    assert n == 0
    assert not (site / "evil.txt").exists()


def test_apply_empty_markdown_returns_zero(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    assert apply_basic_lp_generated_markdown(site_dir=site, markdown="# だけ") == 0


def test_collect_marker_file_blocks(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    md = """<<<FILE app/page.tsx>>>
export default function Page() { return null; }
<<<ENDFILE>>>"""
    assert "app/page.tsx" in collect_generated_files_from_markdown(md)
    n = apply_basic_lp_generated_markdown(site_dir=site, markdown=md)
    assert n == 1
    assert (site / "app" / "page.tsx").read_text(encoding="utf-8").strip().startswith(
        "export default"
    )
