"""
LLM がマーカー形式で返すファイルパスの検証・パース（重い SDK に依存しない）
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# lib/: 色・CTA クラスなどテンプレ由来の .ts ユーティリティを、案件ごとに LLM が上書き可能にする（柔軟性）
_ALLOWED_PATH_PREFIXES = ("app/", "components/", "lib/")

# Cursor 等がリポジトリ内の「テンプレ絶対パス」で <<<FILE>>> を返すことがある。
# 出力先は常に output/sites/<案件>/ 直下なので、テンプレ接頭辞は剥がして app|components|lib に寄せる。
_TEMPLATE_PATH_PREFIXES = (
    "templates/nextjs_template/",
    "./templates/nextjs_template/",
)


def normalize_llm_project_path(raw: str) -> str:
    """<<<FILE>>> 等に付いたテンプレート用プレフィックスを除去し、サイト直下の相対パスに揃える。"""
    rel = raw.replace("\\", "/").strip()
    orig = rel
    for prefix in _TEMPLATE_PATH_PREFIXES:
        if rel.startswith(prefix):
            rel = rel[len(prefix) :]
            break
    if rel.startswith("nextjs_template/"):
        rel = rel[len("nextjs_template/") :]
    if rel != orig and rel:
        logger.info("LLM 出力パスを正規化: %s → %s", orig, rel)
    return rel


def strip_markdown_code_fence(content: str) -> str:
    """
    LLM が <<<FILE>>> 内の本文を Markdown のコードフェンスで囲んだ場合に除去する。
    （例: 先頭 ```tsx / 末尾 ``` があると TS が「モジュールではない」と判定する）
    """
    s = content.strip()
    if not s.startswith("```"):
        return content
    first_nl = s.find("\n")
    if first_nl == -1:
        return content
    body = s[first_nl + 1 :].rstrip()
    if body.endswith("```"):
        body = body[: -3].rstrip()
    return body


def is_safe_llm_project_path(rel: str) -> bool:
    """書き込み許可する相対パスか（ディレクトリトラバーサル防止）"""
    rel = rel.replace("\\", "/").strip()
    if not rel or ".." in rel or rel.startswith("/"):
        return False
    return any(rel.startswith(p) for p in _ALLOWED_PATH_PREFIXES)


def _parse_triple_marker_blocks(text: str) -> dict[str, str]:
    """<<<FILE path>>> ... <<<ENDFILE>>>（空白・大文字小文字ゆるめ）"""
    pattern = re.compile(
        r"<<<\s*FILE\s+([^\n>]+?)\s*>>>\s*(.*?)\s*<<<\s*ENDFILE\s*>>>",
        re.IGNORECASE | re.DOTALL,
    )
    out: dict[str, str] = {}
    for m in pattern.finditer(text):
        path = normalize_llm_project_path(m.group(1).strip())
        body = strip_markdown_code_fence(m.group(2).strip())
        if is_safe_llm_project_path(path):
            out[path] = body
        else:
            logger.warning("LLM が許可外パスを出力しました（スキップ）: %s", path)
    return out


def _parse_double_marker_blocks(text: str) -> dict[str, str]:
    """<<FILE path>> ... <<ENDFILE>>（角括弧が1つ欠けた誤出力向け）"""
    pattern = re.compile(
        r"<<\s*FILE\s+([^\n>]+?)\s*>>\s*(.*?)\s*<<\s*ENDFILE\s*>>",
        re.IGNORECASE | re.DOTALL,
    )
    out: dict[str, str] = {}
    for m in pattern.finditer(text):
        path = normalize_llm_project_path(m.group(1).strip())
        body = strip_markdown_code_fence(m.group(2).strip())
        if is_safe_llm_project_path(path):
            out[path] = body
    return out


def _parse_xml_file_blocks(text: str) -> dict[str, str]:
    """<file path="app/page.tsx">...</file>"""
    pattern = re.compile(
        r'<file\s+path=["\']([^"\']+)["\']\s*>(.*?)</file>',
        re.IGNORECASE | re.DOTALL,
    )
    out: dict[str, str] = {}
    for m in pattern.finditer(text):
        path = normalize_llm_project_path(m.group(1).strip().replace("\\", "/"))
        body = strip_markdown_code_fence(m.group(2).strip())
        if is_safe_llm_project_path(path):
            out[path] = body
    return out


def _parse_fenced_path_blocks(text: str) -> dict[str, str]:
    """
    行頭フェンスの直後にパスだけ書く形式:
    ```tsx app/page.tsx
    ...source...
    ```
    """
    pattern = re.compile(
        r"^```(?:tsx?|ts|jsx?|js|typescript|javascript)\s+"
        r"([a-zA-Z0-9_./-]+\.(?:tsx|ts|jsx|js))\s*\n"
        r"(.*?)^\s*```",
        re.MULTILINE | re.DOTALL,
    )
    out: dict[str, str] = {}
    for m in pattern.finditer(text):
        path = normalize_llm_project_path(m.group(1).strip())
        body = m.group(2).strip()
        if is_safe_llm_project_path(path):
            out[path] = body
    return out


def parse_llm_file_blocks(text: str) -> dict[str, str]:
    """
    形式（優先順・同じパスは先勝ち）:
    1. <<<FILE path>>> ... <<<ENDFILE>>>
    2. <<FILE path>> ... <<ENDFILE>>
    3. <file path="...">...</file>
    4. ```tsx path\\n...```
    """
    if not (text or "").strip():
        return {}
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\ufeff", "")

    merged: dict[str, str] = {}
    for chunk in (
        _parse_triple_marker_blocks(text),
        _parse_double_marker_blocks(text),
        _parse_xml_file_blocks(text),
        _parse_fenced_path_blocks(text),
    ):
        for path, body in chunk.items():
            if path not in merged:
                merged[path] = body
    return merged
