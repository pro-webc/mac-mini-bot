"""ヒアリング抽出バンドル"""
import pytest
from modules.case_extraction import detect_blog_desired, extract_hearing_bundle


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


class TestDetectBlogDesired:
    """先方がブログ実装を明確に希望している場合のみ True。言及なし・曖昧は False。"""

    # --- ヒアリングシートの定型質問 ---

    def test_hearing_q5_positive_hai(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ はい\n") is True

    def test_hearing_q5_positive_yes(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ Yes\n") is True

    def test_hearing_q5_negative_iie(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ いいえ\n") is False

    def test_hearing_q5_negative_no(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ No\n") is False

    def test_hearing_q5_negative_fuyo(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ 不要\n") is False

    def test_hearing_q5_ambiguous_defaults_false(self) -> None:
        assert detect_blog_desired("【5】ブログ機能はご利用になりますか？\n→ 検討中\n") is False

    # --- ブログ言及なし → False ---

    def test_empty_string(self) -> None:
        assert detect_blog_desired() is False

    def test_no_blog_mention_at_all(self) -> None:
        assert detect_blog_desired("会社概要ページは必須\nSNS連携希望") is False

    # --- 全情報源からの検出 ---

    def test_appo_memo_blog_desired(self) -> None:
        assert detect_blog_desired(appo_memo="ブログ機能を希望") is True

    def test_sales_notes_blog_desired(self) -> None:
        assert detect_blog_desired(sales_notes="ブログつけたい旨あり") is True

    def test_hearing_no_but_appo_has_blog(self) -> None:
        """ヒアリングになくてもアポメモで希望 → True"""
        assert detect_blog_desired(
            hearing_sheet_content="SNS連携:はい",
            appo_memo="ブログも利用したいとのこと",
        ) is True

    # --- 否定が明確 ---

    def test_blog_explicitly_unwanted(self) -> None:
        assert detect_blog_desired("ブログは不要です") is False

    def test_blog_iranai(self) -> None:
        assert detect_blog_desired("ブログはいらない") is False

    # --- 自由記述での肯定的言及 ---

    def test_freeform_blog_kibou(self) -> None:
        assert detect_blog_desired("ブログを設置希望") is True

    def test_freeform_blog_tsukete(self) -> None:
        assert detect_blog_desired(appo_memo="ブログつけてほしい") is True

    def test_freeform_blog_hitsuyou(self) -> None:
        assert detect_blog_desired(sales_notes="ブログ機能が必要") is True

    # --- フル hearing + 否定 ---

    def test_full_hearing_negative(self) -> None:
        text = (
            "【4】コーポレートサイトとLPどちら？\n→ コーポレート\n\n"
            "【5】ブログ機能はご利用になりますか？\n→ いいえ\n\n"
            "【6】SNSの連携をしますか？\n→ はい\n"
        )
        assert detect_blog_desired(text) is False


def test_extract_hearing_bundle_with_url() -> None:
    b = extract_hearing_bundle(
        {
            "hearing_sheet_url": "https://example.com/h",
            "appo_memo": "",
        },
        fetch_hearing_sheet=lambda u: f"fetched:{u}",
    )
    assert b.hearing_sheet_content == "fetched:https://example.com/h"
