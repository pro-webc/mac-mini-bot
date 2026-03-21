"""スプレッドシート列番号・ヘッダー検証（API なしの純関数）"""
from __future__ import annotations

import re
from collections.abc import Iterable


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


def hearing_cell_is_eligible_for_mac_mini_bot(text: str) -> bool:
    """
    ヒアリング列（AH）の値が Bot 着手対象か。

    - 空 → 対象外
    - 先頭が http:// または https:// のみ（URL として貼られている）→ 対象外（スキップ）
    - それ以外（本文がセルに直接入っている）→ 対象
    """
    t = (text or "").strip()
    if not t:
        return False
    if re.match(r"^https?://", t, re.IGNORECASE):
        return False
    return True
