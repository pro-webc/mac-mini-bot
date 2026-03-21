"""BASIC 用サイトタイプ（別シート）照合の純関数"""
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


def test_basic_when_g_empty() -> None:
    rows = [
        ["R1", "Acme", "", "", "", "", ""],
    ]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is False
    assert mismatch is None


def test_basic_when_row_missing() -> None:
    rows = [["R1", "Acme", "", "", "", "", "LP"]]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R999", "Acme", skip_header=False
    )
    assert ok is False
    assert mismatch is None


def test_skips_row_when_partner_mismatches_then_matches_next() -> None:
    rows = [
        ["R1", "Other", "", "", "", "", "LP"],
        ["R1", "Acme", "", "", "", "", "LP"],
    ]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is True
    assert mismatch is None


def test_partner_mismatch_sets_note() -> None:
    rows = [
        ["R1", "Wrong", "", "", "", "", "LP"],
    ]
    ok, mismatch = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is False
    assert mismatch is not None
    assert "パートナー名不一致" in mismatch


def test_lp_case_insensitive() -> None:
    rows = [["R1", "Acme", "", "", "", "", " lp "]]
    ok, _ = resolve_basic_lp_from_site_type_rows(
        rows, "R1", "Acme", skip_header=False
    )
    assert ok is True
