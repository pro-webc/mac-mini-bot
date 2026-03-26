"""スプレッドシート列番号・ヘッダー検証（API なしの純関数）"""
from __future__ import annotations

import re
from collections.abc import Iterable

from modules.hearing_url_utils import HEARING_HTTP_URL_RE as _HEARING_URL_IN_CELL


def column_letter_to_index(letters: str) -> int:
    """
    列記号を 0 始まりインデックスに変換（A=0, Z=25, AA=26, AD=29）。
    """
    s = letters.strip().upper()
    if not s or not re.fullmatch(r"[A-Z]+", s):
        raise ValueError(f"無効な列記号: {letters!r}")
    result = 0
    for c in s:
        result = result * 26 + (ord(c) - ord("A") + 1)
    return result - 1


def column_index_to_letters(index: int) -> str:
    """0 始まりインデックスを列記号に変換。"""
    if index < 0:
        raise ValueError("index must be >= 0")
    n = index + 1
    parts: list[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        parts.append(chr(65 + rem))
    return "".join(reversed(parts))


def max_column_index_for_map(column_letters: Iterable[str]) -> int:
    return max(column_letter_to_index(c) for c in column_letters)


def quote_sheet_name_for_a1(sheet_name: str) -> str:
    """
    A1 レンジ用のシート名。Google Sheets API v4 では次のとおり:
    - 英字・数字・アンダースコアのみの識別子（例: Sheet1, MyData）はクォートしない
      （'Sheet1'!1:1 のようにクォートすると環境によって 400 Unable to parse range になる）
    - 日本語・空白・記号・シングルクォートを含む名前はシングルクォートで囲み、' は '' にエスケープ
    """
    s = sheet_name.strip()
    if not s:
        raise ValueError("sheet name is empty")
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s):
        return s
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


def a1_range(sheet_name: str, cell_range: str) -> str:
    """例: a1_range('Sheet1', '1:1') -> \"Sheet1!1:1\""""
    return f"{quote_sheet_name_for_a1(sheet_name)}!{cell_range}"


def normalize_header_label(value: str) -> str:
    """比較用に全角半角スペースを圧縮し小文字化（日本語はそのまま）"""
    return " ".join((value or "").replace("\u3000", " ").split()).casefold()


# ---------------------------------------------------------------------------
# 1行目の見出しから列位置を自動検出する（SpreadsheetClient._resolve_columns で使用）
# ---------------------------------------------------------------------------


def resolve_columns_from_header_row(
    header_row: list[str],
    header_labels: dict[str, str],
    aliases: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    """1行目の見出しテキストから各フィールドの列記号を解決する。

    Args:
        header_row: シート1行目のセル値リスト
        header_labels: field_name → 期待する見出しテキスト
        aliases: alias_field → target_field（同じ列を共有するフィールド）

    Returns:
        (resolved_columns, errors)
        resolved_columns: field_name → 列記号（例: "B"）
        errors: 解決できなかったフィールドのエラーメッセージ
    """
    # 正規化ラベル → 列記号の逆引き（重複チェック付き）
    label_to_letters: dict[str, list[str]] = {}
    for idx, cell in enumerate(header_row):
        norm = normalize_header_label(cell)
        if norm:
            label_to_letters.setdefault(norm, []).append(column_index_to_letters(idx))

    resolved: dict[str, str] = {}
    errors: list[str] = []

    for field, label in header_labels.items():
        norm_label = normalize_header_label(label)
        matches = label_to_letters.get(norm_label, [])
        if len(matches) == 1:
            resolved[field] = matches[0]
        elif len(matches) > 1:
            errors.append(
                f"フィールド {field!r}（見出し {label!r}）が複数列に存在します: "
                f"{', '.join(matches)}（一意にしてください）"
            )
        else:
            errors.append(
                f"フィールド {field!r}（見出し {label!r}）が1行目に見つかりません"
            )

    for alias, target in aliases.items():
        if target in resolved:
            resolved[alias] = resolved[target]
        else:
            errors.append(
                f"エイリアス {alias!r}（→ {target!r}）の参照先が解決できません"
            )

    return resolved, errors


def hearing_cell_is_eligible_for_mac_mini_bot(text: str) -> bool:
    """
    ヒアリング列の値が Bot 着手対象か。

    - 空 → 対象外
    - **URL のみ**（http(s) リンクだけで構成。改行・空白のみ残る）→ 対象外（スキップ）
    - **本文が1文字でも残る**（URL 以外の文字）→ 対象
    """
    t = (text or "").strip()
    if not t:
        return False
    remainder = _HEARING_URL_IN_CELL.sub("", t)
    remainder = re.sub(r"\s+", "", remainder)
    return len(remainder) > 0
