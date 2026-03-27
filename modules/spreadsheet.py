"""Google Sheets連携モジュール"""
from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta
from typing import Any

from config.config import (
    GOOGLE_CLOUD_PROJECT,
    GOOGLE_SHEETS_AUTH_MODE,
    GOOGLE_SHEETS_BASIC_SITE_TYPE_SHEET_NAME,
    GOOGLE_SHEETS_BASIC_SITE_TYPE_SKIP_HEADER,
    GOOGLE_SHEETS_BASIC_SITE_TYPE_SPREADSHEET_ID,
    GOOGLE_SHEETS_CREDENTIALS_PATH,
    GOOGLE_SHEETS_SHEET_NAME,
    GOOGLE_SHEETS_SPREADSHEET_ID,
    SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT,
    SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL,
    SPREADSHEET_HEADER_LABELS,
    SPREADSHEET_MIN_PHASE_DEADLINE,
    SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL,
    SPREADSHEET_REQUIRED_CASE_FIELDS,
    SPREADSHEET_TARGET_AI_STATUS,
)
from config.spreadsheet_schema import (
    BOT_WRITABLE_FIELDS,
    SPREADSHEET_COLUMN_ALIASES,
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
    resolve_columns_from_header_row,
)

logger = logging.getLogger(__name__)


def parse_spreadsheet_phase_deadline_cell(raw: str) -> date | None:
    """
    スプレッドシート T 列（フェーズ期限）の表示値を ``datetime.date`` に正規化する。

    対応例: ``2026-03-27``, ``2026/3/27``, ``3/27/2026``, Google 表示のシリアル値（概ね 40000〜55000）。
    解釈不能・空は ``None``。
    """
    s = (raw or "").strip()
    if not s:
        return None
    token = (
        s.replace("年", "/")
        .replace("月", "/")
        .replace("日", "")
        .split()[0]
        .strip()
    )
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%Y.%m.%d"):
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            continue
    try:
        n = float(s.replace(",", ""))
    except ValueError:
        return None
    if 40000 <= n <= 55000:
        return date(1899, 12, 30) + timedelta(days=int(n))
    return None


def _normalize_site_type_lookup_key(s: str) -> str:
    """照合用に空白を圧縮し casefold（レコード番号・パートナー名の比較用）。"""
    return " ".join((s or "").replace("\u3000", " ").split()).casefold()


def _site_type_row_cell(row: list, idx: int) -> str:
    return row[idx] if len(row) > idx else ""


def _normalize_basic_site_type_g_cell(raw: str) -> str:
    """G列のサイトタイプを比較用に正規化（lp / cp_basic）。"""
    s = (raw or "").strip().lower().replace("\u3000", " ")
    s = " ".join(s.split())
    s = s.replace(" ", "_").replace("-", "_")
    return s


def resolve_basic_lp_from_site_type_rows(
    rows: list[list],
    record_number: str,
    partner_name: str,
    *,
    skip_header: bool,
) -> tuple[bool | None, str | None]:
    """
    サイトタイプ用シートの行から BASIC LP か BASIC-CP かを判定する（API なしの純関数）。

    **B列=パートナー名**で行を探す（主キー）。同一パートナーが複数行あるときは **A列=レコード番号**
    で1行に絞る。G列は ``lp`` → LP（True）、``cp_basic`` → コーポレートBASIC（False）。

    Returns:
        (is_landing_page, mismatch_detail)
        - ``True`` … BASIC_LP
        - ``False`` … BASIC（cp_basic）
        - ``None`` … 行なし・G空欄・未対応の値（呼び出し側は分岐を上書きしない）
    """
    data = rows[1:] if skip_header and rows else list(rows)
    par_n = _normalize_site_type_lookup_key(partner_name)
    if not par_n:
        return None, "パートナー名が空のためサイトタイプシートを参照できません"

    b_hits: list[list] = []
    for row in data:
        b = _normalize_site_type_lookup_key(_site_type_row_cell(row, 1))
        if b == par_n:
            b_hits.append(row)

    if not b_hits:
        return None, f"パートナー名に一致する行がありません（期待={partner_name!r}）"

    row: list
    mismatch_note: str | None = None
    if len(b_hits) == 1:
        row = b_hits[0]
    else:
        rec_n = _normalize_site_type_lookup_key(record_number)
        if rec_n:
            rec_hits = [
                r
                for r in b_hits
                if _normalize_site_type_lookup_key(_site_type_row_cell(r, 0)) == rec_n
            ]
            if len(rec_hits) == 1:
                row = rec_hits[0]
            elif rec_hits:
                row = rec_hits[0]
                mismatch_note = (
                    f"同一パートナー・同一レコードで複数行あり、先頭を使用（record={record_number!r}）"
                )
            else:
                row = b_hits[0]
                mismatch_note = (
                    f"同一パートナーで複数行あり、レコード番号が一致せず先頭行を使用 "
                    f"（期待record={record_number!r} シートA={_site_type_row_cell(b_hits[0], 0)!r}）"
                )
        else:
            row = b_hits[0]
            mismatch_note = (
                "同一パートナーで複数行あり、レコード番号が空のため先頭行を使用"
            )

    g_raw = (_site_type_row_cell(row, 6) or "").strip()
    if not g_raw:
        return None, mismatch_note

    g_norm = _normalize_basic_site_type_g_cell(g_raw)
    if g_norm == "lp":
        return True, mismatch_note
    if g_norm in ("cp_basic", "cpbasic"):
        return False, mismatch_note

    return (
        None,
        (
            (mismatch_note + " / ") if mismatch_note else ""
        )
        + f"G列の値が未対応です: {g_raw!r}（lp または cp_basic を想定）",
    )


def ai_cell_excludes_from_pending_queue(ai_status_raw: str) -> bool:
    """
    ``get_pending_cases`` 用: R 列の表示値が空でなければキュー対象外（True）。

    着手時に "MacBot" が書き込まれる。空欄の行のみ処理対象とする。
    """
    return bool((ai_status_raw or "").strip())


def missing_required_case_fields(case: dict) -> list[str]:
    """必須項目のうち、空（前後空白のみも空）のキーを返す。"""
    missing: list[str] = []
    for key in SPREADSHEET_REQUIRED_CASE_FIELDS:
        v = (case.get(key) or "").strip()
        if not v:
            missing.append(key)
    return missing


def ball_holder_cell_matches_queue_requirement(raw: str) -> bool:
    """
    Q 列（ボール保持者）がキュー条件を満たすか。

    ``SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT`` が空のときは常に True（条件オフ）。
    それ以外はセル値の前後空白除去後がその文字列と完全一致する必要がある。
    """
    req = (SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT or "").strip()
    if not req:
        return True
    return (raw or "").strip() == req


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


# 1行目読み取りの最大列数（自動検出範囲）
_HEADER_SCAN_END_COL = "AZ"


class SpreadsheetClient:
    """Google Sheets APIクライアント

    列位置は ``__init__`` でシート1行目の見出しから自動検出される。
    検出に失敗した場合は ``RuntimeError`` を送出する。
    """

    def __init__(self) -> None:
        self.service: Any = None
        self.spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
        self.sheet_name = GOOGLE_SHEETS_SHEET_NAME
        self._authenticate()
        # 引数: シート1行目 / SPREADSHEET_HEADER_LABELS / SPREADSHEET_COLUMN_ALIASES
        # 処理: 見出しテキストから列記号を自動検出。見つからないフィールドがあれば RuntimeError
        # 出力: self.columns（field→列記号）, self._bot_writable_letters, self._max_col_index
        self.columns = self._resolve_columns()
        self._max_col_index = max_column_index_for_map(self.columns.values())
        self._data_range_end = column_index_to_letters(self._max_col_index)
        self._bot_writable_letters: frozenset[str] = frozenset(
            self.columns[f] for f in BOT_WRITABLE_FIELDS if f in self.columns
        )

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

    # ------------------------------------------------------------------
    # 列位置の自動検出
    # ------------------------------------------------------------------

    def _resolve_columns(self) -> dict[str, str]:
        """1行目の見出しから各フィールドの列位置を自動検出する。

        検出できないフィールドがあれば RuntimeError。
        """
        range_name = a1_range(self.sheet_name, f"A1:{_HEADER_SCAN_END_COL}1")
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
                    raise RuntimeError(_adc_sheets_scope_help("_resolve_columns")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("_resolve_columns")) from e
            raise

        values = result.get("values") or []
        if not values:
            raise RuntimeError(
                f"シート {self.sheet_name!r} の1行目が空です。"
                "SPREADSHEET_HEADER_LABELS に定義された見出しを1行目に設定してください。"
            )

        header_row = values[0]
        columns, errors = resolve_columns_from_header_row(
            header_row, SPREADSHEET_HEADER_LABELS, SPREADSHEET_COLUMN_ALIASES,
        )

        if errors:
            found_headers = [
                f"{normalize_header_label(c)}（列{column_index_to_letters(i)}）"
                for i, c in enumerate(header_row) if (c or "").strip()
            ]
            msg_lines = [
                "スプレッドシート1行目の列見出しから以下のフィールドを検出できませんでした:",
                *[f"  - {e}" for e in errors],
                "",
                f"シート {self.sheet_name!r} で検出した見出し: {found_headers}",
                "",
                "config/spreadsheet_schema.py の SPREADSHEET_HEADER_LABELS に定義された"
                "見出しテキストを1行目に設定してください。",
            ]
            raise RuntimeError("\n".join(msg_lines))

        logger.info(
            "列位置を自動検出しました: %s",
            {f: columns[f] for f in sorted(columns)},
        )
        return columns

    def _assert_bot_writable(self, col_letter: str, context: str) -> None:
        """Bot が書き込み可能な列かを検証する。"""
        if col_letter not in self._bot_writable_letters:
            raise RuntimeError(
                f"Bot は書き込み対象外の列を編集できません（{context}: 列{col_letter}）"
            )

    # ------------------------------------------------------------------
    # BASIC サイトタイプ照合
    # ------------------------------------------------------------------

    def lookup_basic_is_landing_page(self, record_number: str, partner_name: str) -> bool | None:
        """
        BASIC 契約時に別シート（B列=パートナー名・G列=サイトタイプ）を参照する。

        - G列が ``lp``（大小・空白のゆれ可）→ ``True``（BASIC_LP）
        - G列が ``cp_basic`` → ``False``（BASIC・コーポレート1ページ）
        - 行なし・G空欄・未対応の値・API失敗 → ``None``（分岐を上書きしない＝契約列の BASIC のまま）

        ``GOOGLE_SHEETS_BASIC_SITE_TYPE_SPREADSHEET_ID`` が空のときは ``None``。
        """
        sid = GOOGLE_SHEETS_BASIC_SITE_TYPE_SPREADSHEET_ID
        if not sid:
            return None
        sheet = GOOGLE_SHEETS_BASIC_SITE_TYPE_SHEET_NAME
        range_name = a1_range(sheet, "A:G")
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=sid, range=range_name)
                .execute()
            )
        except HttpError as e:
            logger.error(
                "BASIC サイトタイプシートの取得に失敗しました spreadsheet_id=%s… range=%r %s",
                sid[:8],
                range_name,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(
                        _adc_sheets_scope_help("lookup_basic_is_landing_page")
                    ) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(
                        _adc_quota_project_help("lookup_basic_is_landing_page")
                    ) from e
            return None

        values = result.get("values") or []
        is_lp, mismatch = resolve_basic_lp_from_site_type_rows(
            values,
            record_number,
            partner_name,
            skip_header=GOOGLE_SHEETS_BASIC_SITE_TYPE_SKIP_HEADER,
        )
        if mismatch:
            logger.warning("BASIC サイトタイプ照合: %s", mismatch)
        logger.info(
            "BASIC サイトタイプ照合: record=%r partner=%r → "
            "is_landing_page=%s（True=lp / False=cp_basic / None=参照不可・未設定）",
            record_number,
            partner_name,
            is_lp,
        )
        return is_lp

    # ------------------------------------------------------------------
    # 案件取得
    # ------------------------------------------------------------------

    def get_pending_cases(self, sheet_name: str | None = None) -> list[dict]:
        """
        Bot が処理すべき案件を取得（行番号の昇順＝シート上から順）。

        条件（config）:
        - phase_status 列が SPREADSHEET_TARGET_AI_STATUS と完全一致
        - ai_status 列が空欄（``ai_cell_excludes_from_pending_queue`` が False）
        - SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL のとき: ヒアリング列が URL のみの行はスキップ（本文が1文字でもあれば着手）
        - かつ（既定）テストサイトURL列が空
        - かつ SPREADSHEET_MIN_PHASE_DEADLINE 設定時: フェーズ期限日が最小日以降で解釈可能であること
        - かつ SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT 設定時: ball_holder 列がその文字列と完全一致

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

            phase_status = self._cell(row, self.columns["phase_status"]).strip()
            if phase_status != SPREADSHEET_TARGET_AI_STATUS:
                continue
            ai_status = self._cell(row, self.columns["ai_status"])
            if ai_cell_excludes_from_pending_queue(ai_status):
                continue

            if SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL:
                hearing = self._cell(row, self.columns["hearing_sheet_url"])
                if not hearing_cell_is_eligible_for_mac_mini_bot(hearing):
                    logger.debug(
                        "行%s: ヒアリング列が空または URL のためスキップ（本文のみ着手）",
                        row_index,
                    )
                    continue

            if SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL:
                test_site = self._cell(row, self.columns["test_site_url"]).strip()
                if test_site:
                    continue

            ball_holder = self._cell(row, self.columns["ball_holder"])
            if not ball_holder_cell_matches_queue_requirement(ball_holder):
                logger.debug(
                    "行%s: Q列ボール保持者が %r と一致しないためスキップ（実際=%r）",
                    row_index,
                    (SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT or "").strip(),
                    (ball_holder or "").strip()[:80],
                )
                continue

            if SPREADSHEET_MIN_PHASE_DEADLINE is not None:
                pd_raw = self._cell(row, self.columns["phase_deadline"])
                pd_date = parse_spreadsheet_phase_deadline_cell(pd_raw)
                if pd_date is None:
                    logger.debug(
                        "行%s: フェーズ期限日が空または解釈不能のためスキップ（T列=%r）",
                        row_index,
                        pd_raw[:80] if pd_raw else "",
                    )
                    continue
                if pd_date < SPREADSHEET_MIN_PHASE_DEADLINE:
                    logger.debug(
                        "行%s: フェーズ期限日 %s が最小着手日 %s より前のためスキップ",
                        row_index,
                        pd_date.isoformat(),
                        SPREADSHEET_MIN_PHASE_DEADLINE.isoformat(),
                    )
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

        _far_future = date(9999, 12, 31)
        cases.sort(
            key=lambda c: (
                parse_spreadsheet_phase_deadline_cell(c.get("phase_deadline", ""))
                or _far_future,
                int(c["row_number"]),
            )
        )
        logger.info(
            "処理対象案件を %s 件取得（期限日昇順・同日は行番号昇順）target_ai_status=%r "
            "require_empty_test_site_url=%s ball_holder_required=%r min_phase_deadline=%s 一覧=%s",
            len(cases),
            SPREADSHEET_TARGET_AI_STATUS,
            SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL,
            (SPREADSHEET_BALL_HOLDER_REQUIRED_TEXT or "").strip() or "(なし)",
            SPREADSHEET_MIN_PHASE_DEADLINE.isoformat()
            if SPREADSHEET_MIN_PHASE_DEADLINE
            else "(なし)",
            [
                f"row{c['row_number']}={c.get('record_number','?')}(T={c.get('phase_deadline','')[:10]})"
                for c in cases
            ],
        )
        return cases

    def get_case_by_record_number(
        self, record_number: str, *, sheet_name: str | None = None,
    ) -> dict | None:
        """ai_status 列の状態に関係なく、レコード番号で 1 件だけ取得する（再開用）。"""
        sheet = sheet_name or self.sheet_name
        range_name = a1_range(sheet, f"A:{self._data_range_end}")
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])
        want = str(record_number).strip()
        rec_col = self.columns["record_number"]
        for row_index, row in enumerate(values[1:], start=2):
            cell = self._cell(row, rec_col).strip()
            if cell == want:
                return self._parse_row(row, row_index)
        return None

    def _cell(self, row: list, col_letter: str) -> str:
        idx = column_letter_to_index(col_letter)
        return row[idx] if len(row) > idx else ""

    def _parse_row(self, row: list, row_number: int) -> dict:
        """行データをパース"""

        def get_value(col_letter: str) -> str:
            return self._cell(row, col_letter)

        return {
            "row_number": row_number,
            "record_number": get_value(self.columns["record_number"]),
            "partner_name": get_value(self.columns["partner_name"]),
            "contract_plan": get_value(self.columns["contract_plan"]),
            "ball_holder": get_value(self.columns["ball_holder"]),
            "ai_status": get_value(self.columns["ai_status"]),
            "phase_deadline": get_value(self.columns["phase_deadline"]),
            "appo_memo": get_value(self.columns["appo_memo"]),
            "sales_notes": get_value(self.columns["sales_notes"]),
            "hearing_sheet_url": get_value(self.columns["hearing_sheet_url"]),
            "github_repo_url": get_value(self.columns["github_repo_url"]),
            "test_site_url": get_value(self.columns["test_site_url"]),
            "deploy_url": get_value(self.columns["deploy_url"]),
        }

    # ------------------------------------------------------------------
    # 書き込み
    # ------------------------------------------------------------------

    def resolve_current_row(
        self,
        record_number: str,
        partner_name: str,
        *,
        sheet_name: str | None = None,
    ) -> int:
        """レコード番号+パートナー名で現在の行番号を取得する。

        行の挿入・削除で行番号がずれうるため、長時間処理の後で
        スプレッドシートに書き込む前に呼び出す。
        レコード番号が一致し、パートナー名も一致する行を返す。
        パートナー名が不一致の場合は警告を出しつつレコード番号一致を優先する。
        """
        sheet = sheet_name or self.sheet_name
        range_name = a1_range(sheet, f"A:{self._data_range_end}")
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])
        want_rec = str(record_number).strip()
        rec_col = self.columns["record_number"]
        partner_col = self.columns["partner_name"]
        for row_index, row in enumerate(values[1:], start=2):
            cell_rec = self._cell(row, rec_col).strip()
            if cell_rec == want_rec:
                cell_partner = self._cell(row, partner_col).strip()
                if cell_partner != partner_name.strip():
                    logger.warning(
                        "行番号再解決: レコード番号 %r の行 %d でパートナー名が不一致 "
                        "(期待=%r 実際=%r)。レコード番号一致を優先します",
                        want_rec, row_index, partner_name, cell_partner,
                    )
                return row_index
        raise ValueError(
            f"レコード番号 {want_rec!r} がシート {sheet!r} に見つかりません"
        )

    def update_deploy_url(
        self, row_number: int, deploy_url: str, sheet_name: str | None = None
    ) -> None:
        sheet = sheet_name or self.sheet_name
        try:
            col_letter = self.columns["deploy_url"]
            self._assert_bot_writable(col_letter, "update_deploy_url")
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

    def update_deploy_url_and_complete_status(
        self,
        row_number: int,
        deploy_url: str,
        github_repo_url: str = "",
        correction_tool_url: str = "",
        sheet_name: str | None = None,
    ) -> None:
        """
        github_repo_url・deploy_url・correction_tool_url を 1 回の batchUpdate で書く。

        片方だけ更新されて不整合にならないよう、同時に書き込む。
        correction_tool_url が空のときはその列には書き込まない。
        """
        sheet = sheet_name or self.sheet_name
        col_deploy = self.columns["deploy_url"]
        col_github = self.columns["github_repo_url"]
        self._assert_bot_writable(col_deploy, "update_deploy_url_and_complete_status")
        self._assert_bot_writable(col_github, "update_deploy_url_and_complete_status")
        range_deploy = a1_range(sheet, f"{col_deploy}{row_number}")
        range_github = a1_range(sheet, f"{col_github}{row_number}")

        data_entries = [
            {"range": range_github, "values": [[github_repo_url]]},
            {"range": range_deploy, "values": [[deploy_url]]},
        ]
        if correction_tool_url:
            col_correction = self.columns["correction_tool_url"]
            self._assert_bot_writable(col_correction, "update_deploy_url_and_complete_status")
            range_correction = a1_range(sheet, f"{col_correction}{row_number}")
            data_entries.append({"range": range_correction, "values": [[correction_tool_url]]})

        try:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "valueInputOption": "RAW",
                    "data": data_entries,
                },
            ).execute()
            logger.info(
                "GitHub URL・デプロイ URL・修正ツール URL を一括更新しました "
                "sheet=%s row=%s github=%s deploy=%s correction=%s",
                sheet,
                row_number,
                github_repo_url,
                deploy_url,
                correction_tool_url or "(なし)",
            )
        except HttpError as e:
            logger.error(
                "GitHub URL・デプロイ URL 一括更新に失敗しました sheet=%s row=%s %s",
                sheet,
                row_number,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(
                        _adc_sheets_scope_help("update_deploy_url_and_complete_status")
                    ) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(
                        _adc_quota_project_help("update_deploy_url_and_complete_status")
                    ) from e
            raise

    def get_ai_status_cell(self, row_number: int, sheet_name: str | None = None) -> str:
        """
        ai_status 列（Bot 着手フラグ）の表示値を 1 セルだけ取得する。

        複数プロセスで ``main.py`` を並列起動するとき、着手直前に呼び出し
        他ワーカーが既に "MacBot" を書き込んでいないか確認する用途。
        """
        sheet = sheet_name or self.sheet_name
        col_letter = self.columns["ai_status"]
        range_name = a1_range(sheet, f"{col_letter}{row_number}")
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
        except HttpError as e:
            logger.error(
                "ai_status 列（Bot 着手フラグ）の取得に失敗しました sheet=%s row=%s range=%r %s",
                sheet,
                row_number,
                range_name,
                _http_error_detail(e),
                exc_info=True,
            )
            if GOOGLE_SHEETS_AUTH_MODE == "application_default":
                if _is_insufficient_sheets_scope_error(e):
                    raise RuntimeError(_adc_sheets_scope_help("get_ai_status_cell")) from e
                if _is_adc_quota_project_error(e):
                    raise RuntimeError(_adc_quota_project_help("get_ai_status_cell")) from e
            raise
        values = result.get("values") or []
        if not values or not values[0]:
            return ""
        return str(values[0][0] or "").strip()

    def update_ai_status(
        self, row_number: int, status: str, sheet_name: str | None = None
    ) -> None:
        sheet = sheet_name or self.sheet_name
        try:
            col_letter = self.columns["ai_status"]
            self._assert_bot_writable(col_letter, "update_ai_status")
            range_name = a1_range(sheet, f"{col_letter}{row_number}")

            body = {"values": [[status]]}

            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()

            logger.info(
                "ai_status 列（Bot 着手フラグ）を更新しました sheet=%s row=%s col=%s status=%r",
                sheet,
                row_number,
                col_letter,
                status,
            )

        except HttpError as e:
            logger.error(
                "ai_status 列（Bot 着手フラグ）の更新に失敗しました sheet=%s row=%s status=%r %s",
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
