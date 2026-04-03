"""modules.slack_client のテスト"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from modules.slack_client import (
    CorrectionMessage,
    SlackFetchError,
    extract_record_number,
    fetch_correction_messages,
)


# ---------------------------------------------------------------------------
# extract_record_number
# ---------------------------------------------------------------------------


class TestExtractRecordNumber:
    def test_hash_prefix(self) -> None:
        assert extract_record_number("#12345 電話番号を修正して") == "12345"

    def test_bare_number_at_start(self) -> None:
        assert extract_record_number("12345 ヘッダーの色を変更") == "12345"

    def test_hash_only(self) -> None:
        assert extract_record_number("#16887") == "16887"

    def test_five_digit(self) -> None:
        assert extract_record_number("#17274 テキスト修正") == "17274"

    def test_no_match_short(self) -> None:
        assert extract_record_number("#123 短すぎる") is None

    def test_no_match_empty(self) -> None:
        assert extract_record_number("") is None

    def test_no_match_text_only(self) -> None:
        assert extract_record_number("修正してください") is None

    def test_mid_text_hash(self) -> None:
        assert extract_record_number("案件 #15839 の色を変更") == "15839"

    def test_six_digit(self) -> None:
        assert extract_record_number("#123456 修正") == "123456"

    def test_record_number_colon(self) -> None:
        """実データ形式: レコード番号:16960"""
        assert extract_record_number("レコード番号:16960") == "16960"

    def test_record_number_fullwidth_colon(self) -> None:
        """全角コロン形式"""
        assert extract_record_number("レコード番号：16960") == "16960"

    def test_record_number_in_template(self) -> None:
        """テンプレート形式の実データ"""
        text = "【案件情報】\nレコード番号:16960\nパートナー名:ビューティーサロン葵"
        assert extract_record_number(text) == "16960"

    def test_tab_separated(self) -> None:
        """タブ区切り形式: 16800\\tコンドミニアムとらや"""
        assert extract_record_number("16800\tコンドミニアムとらや") == "16800"


# ---------------------------------------------------------------------------
# fetch_correction_messages
# ---------------------------------------------------------------------------


class TestFetchCorrectionMessages:
    def _mock_history(self, messages: list[dict]) -> MagicMock:
        client = MagicMock()
        client.conversations_history.return_value = {"messages": messages}
        client.conversations_replies.return_value = {"messages": []}
        return client

    @patch("modules.slack_client.WebClient")
    def test_filters_by_record_number(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = self._mock_history([
            {"text": "#12345 電話番号修正", "ts": "1000.0", "user": "U1"},
            {"text": "#99999 別の案件", "ts": "1001.0", "user": "U2"},
            {"text": "#12345 色も変更", "ts": "1002.0", "user": "U1"},
        ])
        results = fetch_correction_messages(
            token="xoxb-test", channel_id="C123", record_number="12345",
        )
        assert len(results) == 2
        assert results[0].text == "#12345 電話番号修正"
        assert results[1].text == "#12345 色も変更"

    @patch("modules.slack_client.WebClient")
    def test_empty_channel(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = self._mock_history([])
        results = fetch_correction_messages(
            token="xoxb-test", channel_id="C123", record_number="12345",
        )
        assert results == []

    @patch("modules.slack_client.WebClient")
    def test_no_matching_record(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = self._mock_history([
            {"text": "#99999 別の案件", "ts": "1000.0", "user": "U1"},
        ])
        results = fetch_correction_messages(
            token="xoxb-test", channel_id="C123", record_number="12345",
        )
        assert results == []

    @patch("modules.slack_client.WebClient")
    def test_includes_thread_replies(self, mock_cls: MagicMock) -> None:
        client = MagicMock()
        client.conversations_history.return_value = {"messages": [
            {"text": "#12345 修正依頼", "ts": "1000.0", "user": "U1",
             "thread_ts": "1000.0", "reply_count": 2},
        ]}
        client.conversations_replies.return_value = {"messages": [
            {"text": "#12345 修正依頼", "ts": "1000.0", "user": "U1"},
            {"text": "ヘッダーも直して", "ts": "1000.1", "user": "U2"},
            {"text": "了解です", "ts": "1000.2", "user": "U3"},
        ]}
        mock_cls.return_value = client

        results = fetch_correction_messages(
            token="xoxb-test", channel_id="C123", record_number="12345",
        )
        assert len(results) == 3
        assert not results[0].is_reply
        assert results[1].is_reply
        assert results[1].text == "ヘッダーも直して"
        assert results[2].is_reply

    @patch("modules.slack_client.WebClient")
    def test_sorted_by_ts(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = self._mock_history([
            {"text": "#12345 後のメッセージ", "ts": "2000.0", "user": "U1"},
            {"text": "#12345 先のメッセージ", "ts": "1000.0", "user": "U1"},
        ])
        results = fetch_correction_messages(
            token="xoxb-test", channel_id="C123", record_number="12345",
        )
        assert results[0].ts == "1000.0"
        assert results[1].ts == "2000.0"

    @patch("modules.slack_client.WebClient")
    def test_api_error_raises_slack_fetch_error(self, mock_cls: MagicMock) -> None:
        from slack_sdk.errors import SlackApiError

        client = MagicMock()
        client.conversations_history.side_effect = SlackApiError(
            message="channel_not_found",
            response={"ok": False, "error": "channel_not_found"},
        )
        mock_cls.return_value = client

        with pytest.raises(SlackFetchError, match="channel_not_found"):
            fetch_correction_messages(
                token="xoxb-test", channel_id="C_BAD", record_number="12345",
            )
