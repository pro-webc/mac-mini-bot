"""Google Sheets連携モジュール"""
from __future__ import annotations

import logging
import os
from typing import Any

from config.config import (
    GOOGLE_CLOUD_PROJECT,
    GOOGLE_SHEETS_AUTH_MODE,
    GOOGLE_SHEETS_CREDENTIALS_PATH,
    GOOGLE_SHEETS_SHEET_NAME,
    GOOGLE_SHEETS_SPREADSHEET_ID,
    SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL,
    SPREADSHEET_COLUMNS,
    SPREADSHEET_HEADER_LABELS,
    SPREADSHEET_REQUIRED_CASE_FIELDS,
    SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL,
    SPREADSHEET_TARGET_AI_STATUS,
)
from google.auth import default as google_auth_default
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from modules.spreadsheet_schema import (
    a1_range,
    column_index_to_letters,
    column_letter_to_index,
    hearing_cell_is_eligible_for_mac_mini_bot,
    max_column_index_for_map,
    normalize_header_label,
)

logger = logging.getLogger(__name__)

# Bot が書き込みしてよい列（AV・AW のみ）。それ以外の列は更新しない。
SPREADSHEET_BOT_WRITABLE_LETTERS: frozenset[str] = frozenset(
    {SPREADSHEET_COLUMNS["ai_status"], SPREADSHEET_COLUMNS["deploy_url"]}
)


def _assert_bot_writable_column(col_letter: str, context: str) -> None:
    if col_letter not in SPREADSHEET_BOT_WRITABLE_LETTERS:
        raise RuntimeError(
            f"Bot は AV/AW 以外の列を編集できません（{context}: {col_letter}）"
        )


def missing_required_case_fields(case: dict) -> list[str]:
    """必須項目のうち、空（前後空白のみも空）のキーを返す。"""
    missing: list[str] = []
    for key in SPREADSHEET_REQUIRED_CASE_FIELDS:
        v = (case.get(key) or "").strip()
        if not v:
            missing.append(key)
    return missing


def _is_insufficient_sheets_scope_error(exc: HttpError) -> bool:
    """application_default で Sheets スコープ無しの ADC を使っているときの 403。"""
    if exc.resp.status != 403:
        return False
    body = (getattr(exc, "content", b"") or b"").decode("utf-8", errors="replace")
    return (
        "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in body
        or "insufficient authentication scopes" in body.lower()
    )


def _is_adc_quota_project_error(exc: HttpError) -> bool:
    """ユーザー ADC でクォータプロジェクト未設定のときの 403（Sheets API）。"""
    if exc.resp.status != 403:
        return False
    body = (getattr(exc, "content", b"") or b"").decode("utf-8", errors="replace")
    return (
        "quota project" in body.lower()
        or "requires a quota project" in body.lower()
    )


def _adc_quota_project_help(context: str) -> str:
    return (
        "Google Sheets: Application Default Credentials 利用時は "
        "クォータプロジェクト（GOOGLE_CLOUD_PROJECT）が必須です。\n"
        "  bash scripts/gcloud_set_adc_quota_project.sh YOUR_PROJECT_ID\n"
        "  あわせて .env に GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID を追加し、"
        "そのプロジェクトで Google Sheets API を有効化してください。\n"
        "  gcloud config get-value project が (unset) のときは上記が必要です。\n"
        f"（発生箇所: {context}）"
    )


def _adc_sheets_scope_help(context: str) -> str:
    return (
        "Google Sheets: Application Default Credentials に "
        "Sheets 用スコープがありません。次のいずれかを実行してから再試行してください:\n"
        "  bash scripts/gcloud_application_default_login.sh\n"
        "  または: gcloud auth application-default login "
        "--scopes=https://www.googleapis.com/auth/cloud-platform,"
        "https://www.googleapis.com/auth/spreadsheets\n"
        "（新版 gcloud は cloud-platform と spreadsheets の両方が必要です）\n"
        f"（発生箇所: {context}）"
    )


def _http_error_detail(exc: HttpError) -> str:
    parts: list[str] = []
    if getattr(exc, "resp", None) is not None:
        parts.append(f"status={exc.resp.status}")
    if getattr(exc, "reason", None):
        parts.append(f"reason={exc.reason!r}")
    content = getattr(exc, "content", b"") or b""
    if isinstance(content, bytes):
        tail = content[:800].decode("utf-8", errors="replace")
        if tail.strip():
            parts.append(f"body={tail!r}")
    return " ".join(parts) if parts else repr(exc)


class SpreadsheetClient:
    """Google Sheets APIクライアント"""

    def __init__(self) -> None:
        self.service: Any = None
        self.spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
        self.sheet_name = GOOGLE_SHEETS_SHEET_NAME
        self._max_col_index = max_column_index_for_map(SPREADSHEET_COLUMNS.values())
        self._data_range_end = column_index_to_letters(self._max_col_index)
        self._authenticate()

    def _authenticate(self) -> None:
        """Google Sheets API認証"""
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        try:
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                quota = GOOGLE_CLOUD_PROJECT or None
                credentials, _project = google_auth_default(
                    scopes=scopes,
                    quota_project_id=quota,
                )
                self.service = build(
                    "sheets", "v4", credentials=credentials, cache_discovery=False
                )
                logger.info(
                    "Google Sheets API 認証に成功しました "
                    "(application_default, spreadsheet_id=%s…, sheet=%r)",
                    self.spreadsheet_id[:8] if self.spreadsheet_id else "",
                    self.sheet_name,
                )
                return

            if not os.path.exists(GOOGLE_SHEETS_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"認証情報ファイルが見つかりません: {GOOGLE_SHEETS_CREDENTIALS_PATH}"
                )

            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_PATH,
                scopes=scopes,
            )

            self.service = build(
                "sheets", "v4", credentials=credentials, cache_discovery=False
            )
            logger.info(
                "Google Sheets API 認証に成功しました (service_account, spreadsheet_id=%s…, sheet=%r)",
                self.spreadsheet_id[:8] if self.spreadsheet_id else "",
                self.sheet_name,
            )
        except FileNotFoundError:
            logger.exception(
                "Google Sheets 認証ファイルが存在しません path=%s",
                GOOGLE_SHEETS_CREDENTIALS_PATH,
            )
            raise
        except Exception as e:
            logger.exception(
                "Google Sheets API 認証に失敗しました mode=%s path=%s err=%s",
                GOOGLE_SHEETS_AUTH_MODE,
                GOOGLE_SHEETS_CREDENTIALS_PATH,
                e,
            )
            raise

    def validate_header_labels(self) -> list[str]:
        """
        1行目の列見出しが config の SPREADSHEET_HEADER_LABELS と一致するか検証する。

        Returns:
            不一致メッセージのリスト（空なら OK）
        """
        mismatches: list[str] = []
        # 行だけの 1:1 は Sheet1 のように末尾が数字のシート名と組み合わさると API が
        # "Unable to parse range" になることがあるため、A1〜期待末尾列で明示する。
        range_name = a1_range(self.sheet_name, f"A1:{self._data_range_end}1")
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
        except HttpError as e:
            logger.error(
                "ヘッダー行の取得に失敗しました range=%r %s",
                range_name,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(_adc_sheets_scope_help("validate_header_labels")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("validate_header_labels")) from e
            raise

        values = result.get("values") or []
        if not values:
            msg = f"シート {self.sheet_name!r} の1行目が空です（range={range_name}）"
            logger.error("%s", msg)
            return [msg]

        header_row = values[0]
        logger.info(
            "列見出し検証: sheet=%r 取得セル数=%s (期待末尾列=%s)",
            self.sheet_name,
            len(header_row),
            self._data_range_end,
        )

        for field, letter in SPREADSHEET_COLUMNS.items():
            expected = SPREADSHEET_HEADER_LABELS.get(field)
            if not expected:
                continue
            idx = column_letter_to_index(letter)
            actual = header_row[idx] if idx < len(header_row) else ""
            exp_n = normalize_header_label(expected)
            act_n = normalize_header_label(actual)
            if exp_n != act_n:
                mismatches.append(
                    f"列{letter}（{field}）見出し不一致: 期待 {expected!r} / 実際 {actual!r}"
                )

        if mismatches:
            logger.warning(
                "スプレッドシート列名の整合性: %s 件の不一致（起動時に ERROR/WARN として再出力されます）",
                len(mismatches),
            )
        else:
            logger.info("スプレッドシート列名の整合性チェック: OK")

        return mismatches

    def get_pending_cases(self, sheet_name: str | None = None) -> list[dict]:
        """
        Bot が処理すべき案件を取得（行番号の昇順＝シート上から順）。

        条件（config）:
        - phase_status 列が SPREADSHEET_TARGET_AI_STATUS と完全一致
        - mac-mini 列（AV）が未処理（完了/処理中/エラーでない）
        - SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL のとき: ヒアリング列が本文（http(s) URL だけの行はスキップ）
        - かつ（既定）テストサイトURL列が空

        Args:
            sheet_name: 省略時は GOOGLE_SHEETS_SHEET_NAME

        Returns:
            案件情報のリスト
        """
        sheet = sheet_name or self.sheet_name
        range_name = a1_range(sheet, f"A:{self._data_range_end}")
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
        except HttpError as e:
            logger.error(
                "スプレッドシート全行取得に失敗しました sheet=%r range=%r %s",
                sheet,
                range_name,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(_adc_sheets_scope_help("get_pending_cases")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("get_pending_cases")) from e
            raise

        values = result.get("values", [])
        if not values:
            logger.warning(
                "スプレッドシートにデータがありません sheet=%r range=%r",
                sheet,
                range_name,
            )
            return []

        if not SPREADSHEET_TARGET_AI_STATUS:
            logger.error(
                "SPREADSHEET_TARGET_AI_STATUS が空です。環境変数でフェーズ文字列を設定してください。"
            )
            return []

        cases: list[dict] = []
        for row_index, row in enumerate(values[1:], start=2):
            if len(row) < self._max_col_index + 1:
                logger.debug(
                    "行%s: 列数が推奨より少ない len=%s (推奨>=%s)",
                    row_index,
                    len(row),
                    self._max_col_index + 1,
                )

            phase_status = self._cell(row, SPREADSHEET_COLUMNS["phase_status"]).strip()
            if phase_status != SPREADSHEET_TARGET_AI_STATUS:
                continue
            # mac-mini 列（AV）が既に処理済みなら除外
            ai_status = self._cell(row, SPREADSHEET_COLUMNS["ai_status"]).strip()
            if ai_status in ("完了", "処理中") or ai_status.startswith("エラー"):
                continue

            if SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL:
                hearing = self._cell(row, SPREADSHEET_COLUMNS["hearing_sheet_url"])
                if not hearing_cell_is_eligible_for_mac_mini_bot(hearing):
                    logger.debug(
                        "行%s: ヒアリング列が空または URL のためスキップ（本文のみ着手）",
                        row_index,
                    )
                    continue

            if SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL:
                test_site = self._cell(row, SPREADSHEET_COLUMNS["test_site_url"]).strip()
                if test_site:
                    continue

            case = self._parse_row(row, row_index)
            missing = missing_required_case_fields(case)
            if missing:
                logger.warning(
                    "行%s: 対象フェーズだが必須項目が未入力のため着手しません missing=%s",
                    row_index,
                    missing,
                )
                continue
            cases.append(case)

        cases.sort(key=lambda c: int(c["row_number"]))
        logger.info(
            "処理対象案件を %s 件取得（上から順・行番号昇順）target_ai_status=%r "
            "require_empty_test_site_url=%s 行一覧=%s",
            len(cases),
            SPREADSHEET_TARGET_AI_STATUS,
            SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL,
            [c["row_number"] for c in cases],
        )
        return cases

    def _cell(self, row: list, col_letter: str) -> str:
        idx = column_letter_to_index(col_letter)
        return row[idx] if len(row) > idx else ""

    def _parse_row(self, row: list, row_number: int) -> dict:
        """行データをパース"""

        def get_value(col_letter: str) -> str:
            return self._cell(row, col_letter)

        return {
            "row_number": row_number,
            "record_number": get_value(SPREADSHEET_COLUMNS["record_number"]),
            "partner_name": get_value(SPREADSHEET_COLUMNS["partner_name"]),
            "contract_plan": get_value(SPREADSHEET_COLUMNS["contract_plan"]),
            "ai_status": get_value(SPREADSHEET_COLUMNS["ai_status"]),
            "phase_deadline": get_value(SPREADSHEET_COLUMNS["phase_deadline"]),
            "appo_memo": get_value(SPREADSHEET_COLUMNS["appo_memo"]),
            "sales_notes": get_value(SPREADSHEET_COLUMNS["sales_notes"]),
            "hearing_sheet_url": get_value(SPREADSHEET_COLUMNS["hearing_sheet_url"]),
            "test_site_url": get_value(SPREADSHEET_COLUMNS["test_site_url"]),
            "deploy_url": get_value(SPREADSHEET_COLUMNS["deploy_url"]),
        }

    def update_deploy_url(
        self, row_number: int, deploy_url: str, sheet_name: str | None = None
    ) -> None:
        sheet = sheet_name or self.sheet_name
        try:
            col_letter = SPREADSHEET_COLUMNS["deploy_url"]
            _assert_bot_writable_column(col_letter, "update_deploy_url")
            range_name = a1_range(sheet, f"{col_letter}{row_number}")

            body = {"values": [[deploy_url]]}

            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()

            logger.info(
                "デプロイURLを更新しました sheet=%s row=%s col=%s url=%s",
                sheet,
                row_number,
                col_letter,
                deploy_url,
            )

        except HttpError as e:
            logger.error(
                "デプロイURLの更新に失敗しました sheet=%s row=%s %s",
                sheet,
                row_number,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(_adc_sheets_scope_help("update_deploy_url")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("update_deploy_url")) from e
            raise

    def update_ai_status(
        self, row_number: int, status: str, sheet_name: str | None = None
    ) -> None:
        sheet = sheet_name or self.sheet_name
        try:
            col_letter = SPREADSHEET_COLUMNS["ai_status"]
            _assert_bot_writable_column(col_letter, "update_ai_status")
            range_name = a1_range(sheet, f"{col_letter}{row_number}")

            body = {"values": [[status]]}

            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()

            logger.info(
                "mac-mini 列を更新しました sheet=%s row=%s col=%s status=%r",
                sheet,
                row_number,
                col_letter,
                status,
            )

        except HttpError as e:
            logger.error(
                "mac-mini 列の更新に失敗しました sheet=%s row=%s status=%r %s",
                sheet,
                row_number,
                status,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(_adc_sheets_scope_help("update_ai_status")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("update_ai_status")) from e
            raise
