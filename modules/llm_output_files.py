"""
LLM がマーカー形式で返すファイルパスの検証・パース（重い SDK に依存しない）
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_ALLOWED_PATH_PREFIXES = ("app/", "components/")


def is_safe_llm_project_path(rel: str) -> bool:
    """書き込み許可する相対パスか（ディレクトリトラバーサル防止）"""
    rel = rel.replace("\\", "/").strip()
    if not rel or ".." in rel or rel.startswith("/"):
        return False
    return any(rel.startswith(p) for p in _ALLOWED_PATH_PREFIXES)


def parse_llm_file_blocks(text: str) -> dict[str, str]:
    """
    形式:
    <<<FILE app/page.tsx>>>
    ...content...
    <<<ENDFILE>>>
    """
    pattern = r"<<<FILE\s+([^>]+?)>>>\s*(.*?)\s*<<<ENDFILE>>>"
    out: dict[str, str] = {}
    for m in re.finditer(pattern, text, re.DOTALL):
        path = m.group(1).strip()
        content = m.group(2).strip()
        if is_safe_llm_project_path(path):
            out[path] = content
        else:
            logger.warning("LLM が許可外パスを出力しました（スキップ）: %s", path)
    return out
