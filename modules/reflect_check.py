"""反映率チェック＋欠落補充モジュール。

Manus が GitHub に push したサイトを clone した後、ヒアリング情報との差分を検出し、
欠落があれば Claude CLI でソースコードを直接修正する。
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config.config import REFLECT_CHECK_MODEL

logger = logging.getLogger("reflect_check")

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "config" / "prompts" / "common"


@dataclass
class ReflectItem:
    """反映チェックの各項目。"""

    category: str
    status: str  # "ok", "missing", "partial", "correct_omission"
    expected: str
    found: str = ""
    file_path: str = ""
    detail: str = ""


@dataclass
class ReflectCheckResult:
    """反映チェック全体の結果。"""

    score: float = 0.0
    items: list[ReflectItem] = field(default_factory=list)
    summary: str = ""
    fix_priority: list[str] = field(default_factory=list)
    fixed_count: int = 0

    @property
    def missing_items(self) -> list[ReflectItem]:
        return [i for i in self.items if i.status in ("missing", "partial")]


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------


def _load_prompt(name: str) -> str:
    p = _PROMPTS_DIR / name
    if not p.is_file():
        raise FileNotFoundError(f"プロンプトファイルが見つかりません: {p}")
    return p.read_text(encoding="utf-8")


def _extract_json_from_response(text: str) -> dict[str, Any]:
    """Claude の応答テキストから JSON ブロックを抽出してパースする。"""
    m = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    raw = m.group(1).strip() if m else text.strip()
    # JSON 以外のテキストが混ざっている場合、最初の { から最後の } まで
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    return json.loads(raw)


def _collect_site_source(site_dir: Path) -> str:
    """site_dir 内の TSX/CSS ファイルを連結して返す。"""
    files: list[tuple[str, str]] = []
    for pattern in ("**/*.tsx", "**/*.ts", "**/*.css"):
        for f in sorted(site_dir.glob(pattern)):
            rel = f.relative_to(site_dir)
            # node_modules, .next, llm_raw_output は除外
            parts = rel.parts
            if any(p in ("node_modules", ".next", "llm_raw_output", ".git") for p in parts):
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            files.append((str(rel), content))

    if not files:
        return "(TSXファイルが見つかりません)"

    # トークン制限を考慮して合計文字数を制限（約200K文字）
    MAX_CHARS = 200_000
    parts: list[str] = []
    total = 0
    for rel_path, content in files:
        chunk = f"--- {rel_path} ---\n{content}\n"
        if total + len(chunk) > MAX_CHARS:
            parts.append(f"--- (以降 {len(files) - len(parts)} ファイル省略) ---")
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Step 1: ヒアリング情報の構造化
# ---------------------------------------------------------------------------


def extract_structured_hearing(
    hearing_sheet: str,
    appo_memo: str,
    sales_notes: str,
    *,
    model: str = "",
) -> dict[str, Any]:
    """ヒアリング情報を構造化 JSON に変換する。"""
    from modules.claude_manual_common import generate_text

    _model = model or REFLECT_CHECK_MODEL
    template = _load_prompt("reflect_extract_hearing.txt")
    prompt = (
        template.replace("{{HEARING_SHEET}}", hearing_sheet or "(なし)")
        .replace("{{APPO_MEMO}}", appo_memo or "(なし)")
        .replace("{{SALES_NOTES}}", sales_notes or "(なし)")
    )

    logger.info("ヒアリング情報を構造化中…")
    response = generate_text(prompt, model=_model, module_name="reflect_check")
    structured = _extract_json_from_response(response)
    logger.info(
        "構造化完了: %d 項目",
        sum(1 for v in structured.values() if v and v != [] and v != {}),
    )
    return structured


# ---------------------------------------------------------------------------
# Step 2: 反映率チェック
# ---------------------------------------------------------------------------


def check_reflection(
    structured_hearing: dict[str, Any],
    site_dir: Path,
    *,
    model: str = "",
) -> ReflectCheckResult:
    """構造化ヒアリング情報とサイトソースを比較し、反映率をチェックする。"""
    from modules.claude_manual_common import generate_text

    _model = model or REFLECT_CHECK_MODEL
    template = _load_prompt("reflect_check.txt")
    site_source = _collect_site_source(site_dir)
    prompt = (
        template.replace("{{STRUCTURED_HEARING}}", json.dumps(structured_hearing, ensure_ascii=False, indent=2))
        .replace("{{SITE_SOURCE}}", site_source)
    )

    logger.info("反映率チェック中…")
    response = generate_text(prompt, model=_model, module_name="reflect_check")
    data = _extract_json_from_response(response)

    items = [
        ReflectItem(
            category=item.get("category", ""),
            status=item.get("status", "missing"),
            expected=item.get("expected", ""),
            found=item.get("found", ""),
            file_path=item.get("file_path", ""),
            detail=item.get("detail", ""),
        )
        for item in data.get("items", [])
    ]

    result = ReflectCheckResult(
        score=float(data.get("score", 0.0)),
        items=items,
        summary=data.get("summary", ""),
        fix_priority=data.get("fix_priority", []),
    )

    ok = sum(1 for i in items if i.status in ("ok", "correct_omission"))
    total = len(items) or 1
    logger.info(
        "反映率チェック完了: score=%.1f%% (%d/%d項目反映) missing=%d",
        result.score * 100,
        ok,
        total,
        len(result.missing_items),
    )
    return result


# ---------------------------------------------------------------------------
# Step 3: 欠落補充
# ---------------------------------------------------------------------------


def _parse_fix_response(response: str) -> list[tuple[str, str]]:
    """修正応答から (ファイルパス, 内容) のリストを抽出する。"""
    if "修正不要" in response and len(response) < 50:
        return []

    results: list[tuple[str, str]] = []
    pattern = r"```file:(.+?)\n(.*?)```"
    for m in re.finditer(pattern, response, re.DOTALL):
        file_path = m.group(1).strip()
        content = m.group(2)
        results.append((file_path, content))
    return results


def fix_missing_items(
    check_result: ReflectCheckResult,
    structured_hearing: dict[str, Any],
    site_dir: Path,
    *,
    model: str = "",
) -> int:
    """欠落項目を Claude CLI で修正する。修正ファイル数を返す。"""
    from modules.claude_manual_common import generate_text

    missing = check_result.missing_items
    if not missing:
        logger.info("欠落項目なし — 補充スキップ")
        return 0

    _model = model or REFLECT_CHECK_MODEL
    template = _load_prompt("reflect_fix.txt")

    missing_json = json.dumps(
        [
            {
                "category": item.category,
                "status": item.status,
                "expected": item.expected,
                "found": item.found,
                "detail": item.detail,
            }
            for item in missing
        ],
        ensure_ascii=False,
        indent=2,
    )

    site_source = _collect_site_source(site_dir)
    prompt = (
        template.replace("{{MISSING_ITEMS}}", missing_json)
        .replace("{{SITE_FILES}}", site_source)
    )

    logger.info("欠落 %d 項目の補充中…", len(missing))
    response = generate_text(prompt, model=_model, module_name="reflect_check")

    fixes = _parse_fix_response(response)
    fixed = 0
    for rel_path, content in fixes:
        target = site_dir / rel_path
        if not target.parent.is_dir():
            target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger.info("修正適用: %s (%d chars)", rel_path, len(content))
        fixed += 1

    logger.info("補充完了: %d ファイル修正", fixed)
    return fixed


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------


def run_reflect_check_and_fix(
    hearing_sheet: str,
    appo_memo: str,
    sales_notes: str,
    site_dir: Path,
    *,
    model: str = "",
) -> ReflectCheckResult:
    """反映率チェック＋欠落補充の統合エントリポイント。"""
    _model = model or REFLECT_CHECK_MODEL

    # Step 1: ヒアリング構造化
    structured = extract_structured_hearing(
        hearing_sheet, appo_memo, sales_notes, model=_model,
    )

    # 構造化結果を保存
    raw_dir = site_dir / "llm_raw_output"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "reflect_structured_hearing.json").write_text(
        json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    # Step 2: 反映チェック
    result = check_reflection(structured, site_dir, model=_model)

    # チェック結果を保存
    check_data = {
        "score": result.score,
        "summary": result.summary,
        "fix_priority": result.fix_priority,
        "items": [
            {
                "category": i.category,
                "status": i.status,
                "expected": i.expected,
                "found": i.found,
                "file_path": i.file_path,
                "detail": i.detail,
            }
            for i in result.items
        ],
    }
    (raw_dir / "reflect_check_result.json").write_text(
        json.dumps(check_data, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    # Step 3: 欠落補充
    if result.missing_items:
        result.fixed_count = fix_missing_items(
            result, structured, site_dir, model=_model,
        )
    else:
        logger.info("全項目反映済み — 補充不要")

    return result
