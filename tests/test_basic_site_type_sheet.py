"""BASIC 用サイトタイプ（別シート）照合の純関数

B列=パートナー名で行を特定し、G列が lp → LP / cp_basic → BASIC-CP。
"""
from modules.spreadsheet import resolve_basic_lp_from_site_type_rows


def test_lp_when_g_is_lp() -> None:
    rows = [
        ["id", "name", "", "", "", "", "type"],
        ["R1", "Acme", "", "", "", "", "LP"],
    ]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=True
    )
    assert ok is True
    assert mismatch is None


def test_cp_basic_when_g_is_cp_basic() -> None:
    rows = [["R1", "Acme", "", "", "", "", "cp_basic"]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is False
    assert mismatch is None


def test_partner_only_match_record_differs() -> None:
    """パートナー名が主キー: レコード番号が案件と違っても B が一致すればその行の G を使う。"""
    rows = [["R1", "Acme", "", "", "", "", "lp"]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R999", "Acme", skip_header=False
    )
    assert ok is True
    assert mismatch is None


def test_none_when_g_empty() -> None:
    rows = [["R1", "Acme", "", "", "", "", ""]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is None
    assert mismatch is None


def test_none_when_partner_row_missing() -> None:
    rows = [["R1", "Other", "", "", "", "", "LP"]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is None
    assert mismatch is not None
    assert "パートナー名に一致する行がありません" in mismatch


def test_disambiguate_by_record_when_same_partner_multiple_rows() -> None:
    rows = [
        ["R1", "Acme", "", "", "", "", "lp"],
        ["R2", "Acme", "", "", "", "", "cp_basic"],
    ]
    ok_lp, _ = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok_lp is True
    ok_cp, _ = resolve_basic_lp_from_site_type_rows(
        rows, "R2", "Acme", skip_header=False
    )
    assert ok_cp is False


def test_none_when_unknown_g() -> None:
    rows = [["R1", "Acme", "", "", "", "", "standard"]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is None
    assert mismatch is not None
    assert "未対応" in mismatch


def test_lp_case_insensitive() -> None:
    rows = [["R1", "Acme", "", "", "", "", " lp "]]
    ok, _ = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is True


def test_cp_basic_spacing_variants() -> None:
    rows = [["R1", "Acme", "", "", "", "", "CP BASIC"]]
    ok, _ = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is False
