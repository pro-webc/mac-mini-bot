"""App Router の page.tsx 本数と契約ページ数の突合せ（modules.site_build）"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.site_build import count_app_router_page_tsx_files, verify_site_build


def test_count_app_router_page_tsx_files(tmp_path: Path) -> None:
    (tmp_path / "app" / "about").mkdir(parents=True)
    (tmp_path / "app" / "about" / "page.tsx").write_text("export default function P() {}", encoding="utf-8")
    (tmp_path / "app" / "page.tsx").write_text("export default function H() {}", encoding="utf-8")
    n, rels = count_app_router_page_tsx_files(tmp_path)
    assert n == 2
    assert "app/page.tsx" in rels
    assert "app/about/page.tsx" in rels


def test_verify_site_build_fails_when_page_tsx_exceeds_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "modules.site_build.SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT", True
    )
    (tmp_path / "package.json").write_text('{"scripts":{"build":"echo ok"}}', encoding="utf-8")
    (tmp_path / "app" / "privacy").mkdir(parents=True)
    (tmp_path / "app" / "privacy" / "page.tsx").write_text("export default function P() {}", encoding="utf-8")
    (tmp_path / "app" / "page.tsx").write_text("export default function H() {}", encoding="utf-8")
    ok, log = verify_site_build(tmp_path, skip_install=True, contract_max_pages=1)
    assert ok is False
    assert "契約ページ数" in log
    assert "page.tsx" in log


def test_verify_site_build_skips_count_when_enforcement_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "modules.site_build.SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT", False
    )
    monkeypatch.setattr("modules.site_build.run_npm_build", lambda *_a, **_k: (True, "ok"))
    (tmp_path / "package.json").write_text('{"scripts":{"build":"echo ok"}}', encoding="utf-8")
    (tmp_path / "app" / "a" / "page.tsx").parent.mkdir(parents=True)
    (tmp_path / "app" / "a" / "page.tsx").write_text("export default function P() {}", encoding="utf-8")
    (tmp_path / "app" / "page.tsx").write_text("export default function H() {}", encoding="utf-8")
    ok, _ = verify_site_build(tmp_path, skip_install=True, contract_max_pages=1)
    assert ok is True
