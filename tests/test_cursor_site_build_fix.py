"""Cursor によるビルド修復（プロンプト組み立て）"""
from pathlib import Path

from modules.cursor_site_build_fix import build_fix_prompt


def test_build_fix_prompt_contains_paths(tmp_path: Path) -> None:
    site = tmp_path / "my-site"
    site.mkdir()
    log = "Error: ./app/page.tsx\nSyntax broken\n" * 100
    p = build_fix_prompt(site_dir=site, build_log=log, tail_chars=500)
    assert str(site.resolve()) in p
    assert "Syntax broken" in p or "Error:" in p
