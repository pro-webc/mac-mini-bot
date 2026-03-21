"""必須項目チェック"""
from unittest.mock import patch

from modules.spreadsheet import missing_required_case_fields


def test_missing_required_case_fields_ok() -> None:
    case = {
        "record_number": " R01 ",
        "partner_name": "テスト株式会社",
        "contract_plan": "STANDARD",
    }
    assert missing_required_case_fields(case) == []


def test_missing_required_case_fields_empty() -> None:
    case = {
        "record_number": "",
        "partner_name": "A",
        "contract_plan": "B",
    }
    m = missing_required_case_fields(case)
    assert "record_number" in m


@patch("modules.spreadsheet.SPREADSHEET_REQUIRED_CASE_FIELDS", ("record_number", "partner_name"))
def test_subset_of_fields() -> None:
    assert missing_required_case_fields({"record_number": "1", "partner_name": "x"}) == []
