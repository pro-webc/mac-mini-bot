"""site_generator: 既存サイト削除（rename 退避）"""
from pathlib import Path

from modules.site_generator import _rmtree_existing_site


def test_rmtree_existing_site_removes_dir(tmp_path: Path) -> None:
    site = tmp_path / "demo-site"
    site.mkdir()
    (site / "x.txt").write_text("a", encoding="utf-8")
    _rmtree_existing_site(site)
    assert not site.exists()
    assert not any(tmp_path.glob(".trash-demo-site-*"))


def test_rmtree_existing_site_noop_missing(tmp_path: Path) -> None:
    site = tmp_path / "missing"
    _rmtree_existing_site(site)
    assert not site.exists()
