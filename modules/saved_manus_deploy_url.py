"""Manus 工程テスト／本番 ``llm_raw_output`` 保存から GitHub clone URL を解決する。

``pipeline_test_deploy_only.py`` と pytest が共通利用する。
"""
from __future__ import annotations

from pathlib import Path


def read_deploy_github_url_file(path: Path) -> str:
    """
    ``03_deploy_github_url.txt`` 相当: 先頭の非空・非コメント行を返す。
    """
    text = path.read_text(encoding="utf-8").strip()
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return ""


def normalize_github_clone_url(raw: str) -> str:
    """末尾 ``.git`` を付与し、本番の clone URL 形に揃える。"""
    s = raw.strip().rstrip("/")
    if not s:
        return ""
    if not s.lower().endswith(".git"):
        return f"{s}.git"
    return s


def resolve_github_url_from_manus_output_dir(
    out_dir: Path, *, record_number: str = ""
) -> str:
    """
    ``manus_only_tests/<UTC>/`` または本番 ``llm_raw_output/.../`` から URL を得る。

    1. ``03_deploy_github_url.txt`` の先頭有効行
    2. 空なら ``01_refactored_markdown.md`` を ``split_manus_response_deploy_url`` /
       ``infer_manus_github_clone_url`` で解析
    """
    d = out_dir.resolve()
    p03 = d / "03_deploy_github_url.txt"
    if p03.is_file():
        u = read_deploy_github_url_file(p03).strip()
        if u:
            return u
    p01 = d / "01_refactored_markdown.md"
    if p01.is_file():
        from modules.manus_refactor import (
            infer_manus_github_clone_url,
            split_manus_response_deploy_url,
        )

        text = p01.read_text(encoding="utf-8")
        _body, url = split_manus_response_deploy_url(text)
        if url and url.strip():
            return url.strip()
        inf = infer_manus_github_clone_url(text, record_number=record_number or None)
        if inf:
            return inf
    return ""
