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


def _parse_fence_markdown_to_files(markdown: str) -> dict[str, str]:
    """
    ``` フェンス（先頭行に相対パス）を走査し、(相対パス -> 本文) を得る。

    想定形式:
      ```tsx
      app/page.tsx
      （ソース本文）
      ```
    開始フェンス行がパスのみ（言語タグなし、または `` ```tsx`` 直後の1行目がパス）にも対応。
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


_SINGLE_FENCE_DEFAULT_PATH = "app/page.tsx"
_SINGLE_FENCE_MIN_CHARS = 100


def _extract_unnamed_fence_bodies(markdown: str) -> list[str]:
    """パス判定に関わらず、すべてのコードフェンスの本文を取り出す。"""
    text = (markdown or "").lstrip("\ufeff")
    lines = text.split("\n")
    bodies: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith("```"):
            i += 1
            continue
        i += 1
        body: list[str] = []
        while i < len(lines):
            if lines[i].strip() == "```":
                i += 1
                break
            body.append(lines[i])
            i += 1
        content = "\n".join(body).rstrip()
        if content:
            bodies.append(content + "\n")
    return bodies


def collect_generated_files_from_markdown(markdown: str) -> dict[str, str]:
    """
    生成物マークダウンから (相対パス -> 本文) を集める。

    1. フェンス（パス行付き ``` ブロック）
    2. 0 件なら ``<<<FILE>>>`` / ``<file>`` 等（``parse_llm_file_blocks``）
    3. それでも 0 件で、パスなしの単一フェンスがあれば ``app/page.tsx`` として扱う

    0 件のままなら ``main.process_case`` が ``manus_deploy_github_url`` で shallow clone する。
    """
    mapping = _parse_fence_markdown_to_files(markdown)
    if mapping:
        return mapping
    from modules.llm.llm_output_files import parse_llm_file_blocks

    out: dict[str, str] = {}
    for raw_path, body in parse_llm_file_blocks(markdown).items():
        norm = _normalize_path_candidate(raw_path)
        if _is_allowed_relpath(norm):
            out[norm] = body
    if out:
        return out

    bodies = _extract_unnamed_fence_bodies(markdown)
    if len(bodies) == 1 and len(bodies[0]) >= _SINGLE_FENCE_MIN_CHARS:
        logger.info(
            "collect: パス未指定の単一フェンス(%d chars)を %s として適用",
            len(bodies[0]),
            _SINGLE_FENCE_DEFAULT_PATH,
        )
        return {_SINGLE_FENCE_DEFAULT_PATH: bodies[0]}
    return {}


def apply_basic_lp_generated_markdown(
    *,
    site_dir: Path,
    markdown: str,
) -> int:
    """
    マークダウンから抽出したファイルを ``site_dir`` 以下に書き込む。

    Returns:
        書き込んだファイル数

    """
    site_dir = site_dir.resolve()
    mapping = collect_generated_files_from_markdown(markdown)
    if not mapping:
        raw = (markdown or "").strip()
        tail = raw[:500] + ("…" if len(raw) > 500 else "")
        logger.warning(
            "generated apply: 0 ファイル抽出（フェンス・<<<FILE>>> いずれも該当なし）。"
            " manus_deploy_github_url がある場合は main が shallow clone します。"
            " 先頭抜粋: %r",
            tail,
        )
        return 0
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
            n = apply_basic_lp_generated_markdown(site_dir=site_dir, markdown=md)
            if n:
                return n
            logger.warning(
                "apply_contract_outputs: キー %r は非空(%d chars)だがファイル 0 件"
                " — 次のキーへフォールスルー",
                k,
                len(md),
            )
    return 0


def apply_basic_lp_spec_outputs_to_site_dir(spec: dict, site_dir: Path) -> int:
    """
    ``spec`` に含まれる BASIC LP 生成物を優先順で site_dir に適用する。

    優先: ``basic_lp_refactored_source_markdown`` → 無ければ ``basic_lp_manual_gemini_final``
    """
    return apply_contract_outputs_to_site_dir(
        spec, site_dir, work_branch=ContractWorkBranch.BASIC_LP
    )
