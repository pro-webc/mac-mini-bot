"""ヒアリング抽出バンドル"""
from modules.case_extraction import extract_hearing_bundle


def test_extract_hearing_bundle_without_url() -> None:
    b = extract_hearing_bundle(
        {
            "row_number": 1,
            "record_number": "R1",
            "partner_name": "テスト",
            "contract_plan": "BASIC",
            "appo_memo": "メモA",
            "sales_notes": "メモB",
        },
        fetch_hearing_sheet=lambda _u: "should-not-run",
    )
    assert b.hearing_sheet_content == ""
    assert b.appo_memo == "メモA"
    assert b.sales_notes == "メモB"


def test_extract_hearing_bundle_with_url() -> None:
    b = extract_hearing_bundle(
        {
            "hearing_sheet_url": "https://example.com/h",
            "appo_memo": "",
        },
        fetch_hearing_sheet=lambda u: f"fetched:{u}",
    )
    assert b.hearing_sheet_content == "fetched:https://example.com/h"
