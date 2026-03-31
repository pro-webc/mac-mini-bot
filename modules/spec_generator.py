"""ヒアリングシート取得（`fetch_hearing_sheet`）と、仕様入力ブリーフの組み立て。

本番の案件処理で仕様を得る入口は ``modules.llm.text_llm_stage.run_text_llm_stage``（フェーズ2）。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

import requests

from modules.hearing_url_utils import HEARING_HTTP_URL_RE, HEARING_PASTE_BODY_MIN_LEN

logger = logging.getLogger(__name__)

# Google Sheets URL から spreadsheet_id / gid / 列範囲を抽出する正規表現
_GSHEETS_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9_-]+)")
_GSHEETS_GID_RE = re.compile(r"gid=(\d+)")
_GSHEETS_RANGE_RE = re.compile(r"range=([A-Z]{1,3}:[A-Z]{1,3})")


def _looks_like_html(text: str) -> bool:
    """レスポンス本文やセル貼り付けが HTML かざっくり判定する。"""
    s = (text or "").lstrip()
    if len(s) < 3 or s[0] != "<":
        return False
    head = s[:4000].lower()
    return (
        "<!doctype html" in head
        or "<html" in head
        or "<head" in head
        or "<body" in head
    )


def _html_to_plain_text(html: str) -> str:
    """HTML を LLM 投入用のプレーンテキストに正規化する（タグ・script/style を除去）。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines()]
    out = "\n".join(ln for ln in lines if ln)
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.strip()


def _http_response_as_plain_text(response: requests.Response) -> str:
    """Content-Type または本文先頭から HTML を判定し、プレーンテキストで返す。"""
    raw = response.text or ""
    ct = (response.headers.get("Content-Type") or "").lower()
    if (
        "text/html" in ct
        or "application/xhtml" in ct
        or _looks_like_html(raw)
    ):
        plain = _html_to_plain_text(raw)
        if plain:
            return plain
        logger.warning(
            "HTML と判定したが本文抽出後が空でした（先頭 %s 文字）",
            min(len(raw), 120),
        )
        return raw
    return raw


def _maybe_strip_html_pasted_text(text: str) -> str:
    """スプレッドシートセルに HTML が貼られている場合のみテキスト化。"""
    raw = text or ""
    if _looks_like_html(raw):
        plain = _html_to_plain_text(raw)
        if plain:
            logger.info(
                "ヒアリング列の本文を HTML とみなしテキスト化しました（先頭 %s 文字）",
                min(len(raw), 200),
            )
            return plain
    return raw


def _briefing_value_as_text(v: Any) -> str:
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(v)
    return str(v)


def _plan_info_as_briefing_lines(plan_info: Dict[str, Any]) -> str:
    lines: list[str] = []
    for k in sorted(plan_info.keys()):
        v = plan_info.get(k)
        if v is None or v == "":
            continue
        lines.append(f"- {k}: {_briefing_value_as_text(v)}")
    return "\n".join(lines) if lines else "（項目なし）"


def compose_spec_input_briefing(
    *,
    partner_name: str,
    contract_plan: str,
    contract_pages: int,
    page_rule: str,
    plan_info: Dict[str, Any],
    hearing_sheet_content: str,
    site_build_prompt: str,
    requirements_result: Dict[str, Any],
    max_chars: int = 120_000,
) -> str:
    """
    仕様生成向けの入力を **JSONではなくプレーンテキスト1本**にまとめる（テスト・手動検証用）。
    （出力形式は Markdown サイト台本＋末尾 YAML。レガシー運用では JSON のみも解釈可）
    """
    chunks: list[str] = []
    chunks.append("【パートナー名】")
    chunks.append((partner_name or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約プラン（システム）】")
    chunks.append((contract_plan or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約ページ数（厳守・変更禁止）】")
    chunks.append(str(contract_pages))
    chunks.append("")
    chunks.append("【ページ構成に関する指示】")
    chunks.append(page_rule.strip())
    chunks.append("")
    chunks.append("【契約プラン詳細（システム・テキスト化）】")
    chunks.append(_plan_info_as_briefing_lines(plan_info))
    chunks.append("")
    chunks.append("【ヒアリング原文】")
    chunks.append((hearing_sheet_content or "").strip() or "（空）")
    chunks.append("")
    chunks.append("【サイト制作マスタープロンプト（最優先）】")
    chunks.append(site_build_prompt.strip())
    chunks.append("")

    pt = requirements_result.get("plan_type")
    if pt:
        chunks.append("【システム確定 plan_type】")
        chunks.append(str(pt))
        chunks.append("")

    cm = requirements_result.get("contract_max_pages")
    if cm is not None:
        chunks.append("【contract_max_pages（参照）】")
        chunks.append(str(cm))
        chunks.append("")

    cv = requirements_result.get("client_voice")
    if isinstance(cv, str) and cv.strip():
        sbp_head = site_build_prompt.strip()[:400]
        if cv.strip()[:400] != sbp_head:
            chunks.append("【client_voice（補足・テキスト）】")
            chunks.append(cv.strip())
            chunks.append("")

    ibn = requirements_result.get("internal_build_notes")
    if isinstance(ibn, list) and ibn:
        chunks.append("【内部メモ（サイト非掲載・参照のみ）】")
        for x in ibn:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    oq = requirements_result.get("open_questions")
    if isinstance(oq, list) and oq:
        chunks.append("【要確認事項】")
        for x in oq:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    facts = requirements_result.get("facts")
    if isinstance(facts, dict) and facts:
        chunks.append("【補足ファクト（テキスト化）】")
        for fk, fv in facts.items():
            if fv is None or fv == "":
                continue
            if isinstance(fv, list):
                chunks.append(f"- {fk}:")
                for it in fv:
                    chunks.append(f"  - {it}")
            else:
                chunks.append(f"- {fk}: {_briefing_value_as_text(fv)}")
        chunks.append("")

    out = "\n".join(chunks).strip()
    if len(out) > max_chars:
        logger.warning(
            "仕様入力ブリーフが長いため %s 文字に切り詰めました（元 %s）",
            max_chars,
            len(out),
        )
        half = max_chars // 2 - 80
        out = (
            out[:half]
            + "\n\n…[truncated]…\n\n"
            + out[-half:]
        )
    return out


def _fetch_google_sheet_via_api(
    sheets_service: Any,
    url: str,
) -> Optional[str]:
    """Google Sheets URL を Sheets API で読み込み、質問＋回答をテキスト化して返す。

    Args:
        sheets_service: ``googleapiclient`` の sheets v4 service オブジェクト
        url: ``https://docs.google.com/spreadsheets/d/<ID>/edit...`` 形式
    Returns:
        セル値を改行連結したテキスト。読み取り不可なら None。
    """
    m_id = _GSHEETS_ID_RE.search(url)
    if not m_id:
        return None
    spreadsheet_id = m_id.group(1)

    m_gid = _GSHEETS_GID_RE.search(url)
    gid = int(m_gid.group(1)) if m_gid else 0

    # gid → シート名を解決
    try:
        meta = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="sheets.properties")
            .execute()
        )
    except Exception as exc:
        logger.warning("ヒアリング Sheets メタデータ取得失敗 spreadsheet_id=%s: %s", spreadsheet_id, exc)
        return None

    target_sheet: Optional[str] = None
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("sheetId") == gid:
            target_sheet = props.get("title")
            break
    if target_sheet is None:
        sheets_list = [s["properties"]["title"] for s in meta.get("sheets", [])]
        if sheets_list:
            target_sheet = sheets_list[0]
            logger.info("gid=%s に一致するシートがないため先頭シート %r を使用", gid, target_sheet)
        else:
            return None

    # URL に range= が含まれていればその列、なければ全列
    m_range = _GSHEETS_RANGE_RE.search(url)
    col_range = m_range.group(1) if m_range else "A:Z"
    api_range = f"{target_sheet}!{col_range}"

    try:
        result = (
            sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=api_range)
            .execute()
        )
    except Exception as exc:
        logger.warning("ヒアリング Sheets データ取得失敗 range=%s: %s", api_range, exc)
        return None

    values = result.get("values", [])
    if not values:
        return None

    lines: list[str] = []
    for row in values:
        row_text = "\t".join(str(c) for c in row).strip()
        if row_text:
            lines.append(row_text)

    text = "\n".join(lines)
    logger.info(
        "ヒアリング Sheets API で取得しました sheet=%r range=%s 行数=%s 文字数=%s",
        target_sheet,
        col_range,
        len(values),
        len(text),
    )
    return text


class SpecGenerator:
    """ヒアリングシート取得（セル URL / 長文貼り付け）。"""

    def __init__(self, *, sheets_service: Any = None) -> None:
        self._sheets_service = sheets_service

    def fetch_hearing_sheet(self, url: str) -> Optional[str]:
        """
        ヒアリングシートの内容を取得

        Args:
            url: セル値。先頭が ``http(s)://`` ならその URL を取得する。
                それ以外で **十分長い** 場合はフォーム回答のコピペ本文とみなし、
                文中に参考サイトの URL があっても **取得せず全文を返す**。

        Returns:
            ヒアリングシートの内容（テキスト）
        """
        try:
            raw = (url or "").strip()
            if not raw:
                return None
            # セルに全文が貼られているだけの場合（http で始まらない）
            if not re.match(r"^https?://", raw, re.IGNORECASE):
                if len(raw) >= HEARING_PASTE_BODY_MIN_LEN:
                    logger.info(
                        "ヒアリング列が長文（%s 文字以上）のため、セル全文を本文とします（文中 URL は取得しません）",
                        HEARING_PASTE_BODY_MIN_LEN,
                    )
                    return _maybe_strip_html_pasted_text(raw)
                m = HEARING_HTTP_URL_RE.search(raw)
                if m:
                    fetched = self.fetch_hearing_sheet(m.group(0))
                    if (fetched or "").strip():
                        return fetched
                    logger.warning(
                        "ヒアリング列内の URL 取得が空のため、セル全文を本文として使用します（先頭 %s 文字）",
                        min(len(raw), 200),
                    )
                    return _maybe_strip_html_pasted_text(raw)
                logger.info(
                    "ヒアリングシート列が URL ではないため、本文としてそのまま使用します（先頭 %s 文字）",
                    min(len(raw), 200),
                )
                return _maybe_strip_html_pasted_text(raw)

            # Google Sheets URL → Sheets API で読み込み（認証済みサービスがある場合）
            if "docs.google.com/spreadsheets" in raw and self._sheets_service:
                api_text = _fetch_google_sheet_via_api(self._sheets_service, raw)
                if api_text:
                    return api_text
                logger.warning(
                    "Sheets API での取得に失敗したため HTTP フォールバックを試みます URL=%s",
                    raw[:120],
                )

            # その他の URL / Sheets API フォールバック
            response = requests.get(raw, timeout=60, headers={"User-Agent": "MacMiniBot/1.0"})
            if response.status_code != 200:
                logger.warning(
                    "ヒアリング URL 取得失敗 status=%s URL=%s",
                    response.status_code,
                    raw[:120],
                )
                return None
            text = _http_response_as_plain_text(response)
            if "docs.google.com/spreadsheets" in raw:
                logger.info("ヒアリングシートを HTTP 経由で取得しました（HTML テキスト化、品質に注意）")
            return text
        except Exception as e:
            logger.error("ヒアリングシート取得エラー: %s URL=%s", e, (url or "")[:120])
            return None
