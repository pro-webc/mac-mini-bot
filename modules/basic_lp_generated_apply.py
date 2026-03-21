"""プラン別: Gemini 等が出したマークダウン（パス付きフェンス）を site_dir に書き込む。"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from modules.contract_workflow import ContractWorkBranch

logger = logging.getLogger(__name__)

# 書き込みを許可する相対パス（.. やサイト外への脱出を禁止したうえで）
_ALLOWED_PREFIXES = (
    "app/",
    "public/",
    "components/",
    "lib/",
    "styles/",
)
_ROOT_FILES = frozenset(
    {
        "package.json",
        "next.config.ts",
        "next.config.js",
        "next.config.mjs",
        "tailwind.config.ts",
        "tailwind.config.js",
        "postcss.config.mjs",
        "postcss.config.cjs",
        "tsconfig.json",
        "middleware.ts",
        ".eslintrc.json",
        "next-env.d.ts",
    }
)


def _is_allowed_relpath(rel: str) -> bool:
    r = rel.strip().lstrip("/").replace("\\", "/")
    if not r or r.startswith("..") or "/../" in f"/{r}/":
        return False
    if r in _ROOT_FILES:
        return True
    return any(r.startswith(p) for p in _ALLOWED_PREFIXES)


def _normalize_path_candidate(line: str) -> str:
    """LLM がよく付ける接頭辞・表記ゆれを除去し、許可プレフィックス判定用の相対パスにする。"""
    s = (line or "").strip().lstrip("\ufeff")
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()
    low = s.lower()
    if low.startswith("file:"):
        s = s[5:].strip()
    elif low.startswith("path:"):
        s = s[5:].strip()
    s = s.lstrip("/")
    if s.startswith("./"):
        s = s[2:]
    s = s.replace("\\", "/")
    if s.startswith("src/app/"):
        s = "app/" + s[len("src/app/") :]
    return s


def _is_probable_path_line(line: str) -> bool:
    s = _normalize_path_candidate(line)
    if not s or len(s) > 260:
        return False
    if s.startswith(("-", "*", "|", "#", "import ", "export ", '"', "'", "`", "{", "<")):
        return False
    if " " in s and not s.startswith("app/"):
        return False
    if not re.search(
        r"\.(tsx?|jsx?|css|json|mjs|cjs|md|svg)$", s, re.IGNORECASE
    ) and s not in _ROOT_FILES:
        if "/" not in s:
            return False
    return _is_allowed_relpath(s)


def _safe_target_file(site_dir: Path, rel: str) -> Path:
    site_resolved = site_dir.resolve()
    rel_norm = rel.strip().lstrip("/").replace("\\", "/")
    if not _is_allowed_relpath(rel_norm):
        raise ValueError(f"許可されていないパス: {rel!r}")
    for part in Path(rel_norm).parts:
        if part == "..":
            raise ValueError(f"不正なパス: {rel!r}")
    out = (site_dir / rel_norm).resolve()
    if not str(out).startswith(str(site_resolved)):
        raise ValueError(f"サイトディレクトリ外: {rel!r}")
    return out


def parse_generated_markdown_to_files(markdown: str) -> dict[str, str]:
    """
    マークダウン内の ``` フェンスを走査し、(相対パス -> 本文) を得る。

    想定形式:
      ```tsx
      app/page.tsx
      （ソース本文）
      ```
    または開始行が ``app/page.tsx`` のみで言語タグなし。
    開始フェンスのメタにパスだけがある場合（例: ```app/page.tsx）にも対応。
    """
    text = (markdown or "").lstrip("\ufeff")
    lines = text.split("\n")
    files: dict[str, str] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped.startswith("```"):
            i += 1
            continue
        opener = stripped[3:].strip()
        i += 1
        body: list[str] = []
        path: str | None = None

        if opener and _is_probable_path_line(opener):
            path = _normalize_path_candidate(opener)

        while i < len(lines):
            if lines[i].strip() == "```":
                i += 1
                break
            ln = lines[i]
            if path is None:
                cand = ln.strip()
                if not cand:
                    i += 1
                    continue
                if _is_probable_path_line(cand):
                    path = _normalize_path_candidate(cand)
                    i += 1
                    continue
            body.append(ln)
            i += 1

        content = "\n".join(body).rstrip() + ("\n" if body else "")
        if path and _is_allowed_relpath(path):
            if path in files:
                logger.warning("generated apply: 同一パスが複数回 — 後勝ち %s", path)
            files[path] = content
        elif path:
            logger.debug("generated apply: スキップ（非許可パス） %s", path)
        else:
            preview = (opener + " / " + content[:80]).replace("\n", " ")
            logger.debug(
                "generated apply: フェンスをパス付きファイルとして解釈できずスキップ: %s",
                preview[:200],
            )
    return files


def apply_basic_lp_generated_markdown(
    *,
    site_dir: Path,
    markdown: str,
) -> int:
    """
    マークダウンから抽出したファイルを ``site_dir`` 以下に書き込む。

    Returns:
        書き込んだファイル数

    Raises:
        RuntimeError: 1件も書けなかった場合
    """
    site_dir = site_dir.resolve()
    mapping = parse_generated_markdown_to_files(markdown)
    if not mapping:
        raw = (markdown or "").strip()
        tail = raw[:500] + ("…" if len(raw) > 500 else "")
        logger.error(
            "generated apply: 0 ファイル抽出。フェンス内の1行目に app/page.tsx 等の相対パスが必要です。"
            " 先頭抜粋: %r",
            tail,
        )
        raise RuntimeError(
            "マークダウンからファイルを1件も抽出できませんでした。"
            " 各 ``` ブロックの直後に app/・public/・components/ から始まるパス行を置いてください。"
        )
    n = 0
    for rel in sorted(mapping.keys(), key=lambda x: (x.count("/"), x)):
        content = mapping[rel]
        target = _safe_target_file(site_dir, rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        n += 1
        logger.info("generated apply: 書き込み %s", rel)
    return n


def apply_contract_outputs_to_site_dir(
    spec: dict,
    site_dir: Path,
    *,
    work_branch: ContractWorkBranch,
) -> int:
    """
    契約分岐に応じた ``spec`` キーからマークダウンを取り、site_dir に適用する。

    - BASIC_LP: ``basic_lp_refactored_source_markdown`` → ``basic_lp_manual_gemini_final``
    - BASIC: ``basic_refactored_source_markdown`` → ``basic_manual_gemini_final``
    - STANDARD: ``standard_refactored_source_markdown`` → ``standard_manual_gemini_final``
    - ADVANCE: ``advance_refactored_source_markdown`` → ``advance_manual_gemini_final``
    - その他: 0（スキップ）
    """
    if work_branch == ContractWorkBranch.BASIC_LP:
        keys = ("basic_lp_refactored_source_markdown", "basic_lp_manual_gemini_final")
    elif work_branch == ContractWorkBranch.BASIC:
        keys = ("basic_refactored_source_markdown", "basic_manual_gemini_final")
    elif work_branch == ContractWorkBranch.STANDARD:
        keys = ("standard_refactored_source_markdown", "standard_manual_gemini_final")
    elif work_branch == ContractWorkBranch.ADVANCE:
        keys = ("advance_refactored_source_markdown", "advance_manual_gemini_final")
    else:
        return 0
    for k in keys:
        md = (spec.get(k) or "").strip()
        if md:
            return apply_basic_lp_generated_markdown(site_dir=site_dir, markdown=md)
    return 0


def apply_basic_lp_spec_outputs_to_site_dir(spec: dict, site_dir: Path) -> int:
    """
    ``spec`` に含まれる BASIC LP 生成物を優先順で site_dir に適用する。

    優先: ``basic_lp_refactored_source_markdown`` → 無ければ ``basic_lp_manual_gemini_final``
    """
    return apply_contract_outputs_to_site_dir(
        spec, site_dir, work_branch=ContractWorkBranch.BASIC_LP
    )
