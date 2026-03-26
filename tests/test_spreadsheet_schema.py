"""列記号変換・ヘッダー自動検出"""
import pytest
from modules.spreadsheet_schema import (
    a1_range,
    column_index_to_letters,
    column_letter_to_index,
    hearing_cell_is_eligible_for_mac_mini_bot,
    max_column_index_for_map,
    normalize_header_label,
    quote_sheet_name_for_a1,
    resolve_columns_from_header_row,
)


@pytest.mark.parametrize(
    "letters,index",
    [
        ("A", 0),
        ("B", 1),
        ("Z", 25),
        ("AA", 26),
        ("AD", 29),
        ("AK", 36),
        ("AV", 47),
        ("AW", 48),
    ],
)
def test_column_letter_roundtrip(letters: str, index: int) -> None:
    assert column_letter_to_index(letters) == index
    assert column_index_to_letters(index) == letters


def test_max_column_index() -> None:
    m = max_column_index_for_map(["B", "M", "AD", "AK", "AV", "AW"])
    assert m == 48


def test_normalize_header_label() -> None:
    assert normalize_header_label("  AI統合　ステータス  ") == normalize_header_label(
        "AI統合 ステータス"
    )


def test_invalid_column() -> None:
    with pytest.raises(ValueError):
        column_letter_to_index("1")


def test_quote_sheet_name_for_a1() -> None:
    assert quote_sheet_name_for_a1("Sheet1") == "Sheet1"
    assert quote_sheet_name_for_a1("案件一覧") == "'案件一覧'"
    assert quote_sheet_name_for_a1("O'Reilly") == "'O''Reilly'"
    assert quote_sheet_name_for_a1("MyData") == "MyData"


def test_a1_range() -> None:
    assert a1_range("Sheet1", "1:1") == "Sheet1!1:1"
    assert a1_range("データ", "A:Z") == "'データ'!A:Z"


@pytest.mark.parametrize(
    "text,eligible",
    [
        ("", False),
        ("  ", False),
        ("https://example.com", False),
        ("http://a.jp/x", False),
        ("https://a.com\nhttps://b.com", False),
        ("本文のみ", True),
        ("説明\nhttps://x.com", True),
        ("先頭URLだが本文あり https://x.com 続き", True),
    ],
)
def test_hearing_cell_eligible(text: str, eligible: bool) -> None:
    assert hearing_cell_is_eligible_for_mac_mini_bot(text) is eligible


# ---------------------------------------------------------------------------
# resolve_columns_from_header_row
# ---------------------------------------------------------------------------


def test_resolve_columns_basic() -> None:
    """正常系: 全フィールドが1行目から検出できる。"""
    labels = {"name": "Name", "age": "Age"}
    header = ["ID", "Name", "Age", "Email"]
    cols, errors = resolve_columns_from_header_row(header, labels, {})
    assert errors == []
    assert cols == {"name": "B", "age": "C"}


def test_resolve_columns_with_alias() -> None:
    """エイリアスが正しく解決される。"""
    labels = {"url": "site_url"}
    aliases = {"deploy": "url"}
    header = ["ID", "site_url"]
    cols, errors = resolve_columns_from_header_row(header, labels, aliases)
    assert errors == []
    assert cols["url"] == "B"
    assert cols["deploy"] == "B"


def test_resolve_columns_missing_field() -> None:
    """見出しが見つからないフィールドはエラー。"""
    labels = {"name": "Name", "missing": "NotHere"}
    header = ["ID", "Name"]
    cols, errors = resolve_columns_from_header_row(header, labels, {})
    assert len(errors) == 1
    assert "missing" in errors[0]
    assert "name" in cols


def test_resolve_columns_duplicate_header() -> None:
    """同じ見出しが複数列にあるとエラー。"""
    labels = {"name": "Name"}
    header = ["Name", "Other", "Name"]
    cols, errors = resolve_columns_from_header_row(header, labels, {})
    assert len(errors) == 1
    assert "複数列" in errors[0]


def test_resolve_columns_normalization() -> None:
    """全角空白や大小文字の違いは吸収される。"""
    labels = {"status": "Overall Status"}
    header = ["id", "overall　status"]
    cols, errors = resolve_columns_from_header_row(header, labels, {})
    assert errors == []
    assert cols["status"] == "B"
