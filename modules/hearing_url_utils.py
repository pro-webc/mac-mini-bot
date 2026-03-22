"""ヒアリング列（AH）の本文・URL 解釈を `spec_generator` / マニュアル / スキーマで共有する。

長文のフォーム回答コピペでは、文中の「参考サイト」設問付近の URL を優先し、
先頭に現れる無関係な URL や添付パスに引っ張られないようにする。
"""
from __future__ import annotations

import re

# ``fetch_hearing_sheet`` と同一閾値（長文＝コピペ本文とみなす）
HEARING_PASTE_BODY_MIN_LEN = 400

# ``spec_generator.fetch_hearing_sheet`` の文中 URL 検出と整合
HEARING_HTTP_URL_RE = re.compile(r"https?://[^\s\]<>\")]+", re.IGNORECASE)


def first_http_url_in_text(text: str) -> str:
    """文中の最初の http(s) URL（末尾の句読点のみ除去）。"""
    m = HEARING_HTTP_URL_RE.search(text or "")
    return m.group(0).rstrip(".,;") if m else ""


def reference_site_url_from_hearing(text: str) -> str:
    """
    マニュアルの「参考サイトURL」プレースホルダ用。

    短文セルでは先頭 URL。長文では設問「希望する雰囲気のサイトのURL」直後などを優先。
    """
    t = (text or "").strip()
    if len(t) < HEARING_PASTE_BODY_MIN_LEN:
        return first_http_url_in_text(t)
    patterns = (
        r"希望する雰囲気のサイトのURL[^\n]*\n\s*(https?://[^\s\]<>\")]+)",
        r"希望する[^\n]{0,40}サイト[^\n]{0,20}URL[^\n]*\n\s*(https?://[^\s\]<>\")]+)",
    )
    for p in patterns:
        m = re.search(p, t, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).rstrip(".,;")
    return first_http_url_in_text(t)


def existing_site_url_guess_from_hearing(text: str) -> str:
    """
    既存サイト URL 列が空のときの推測。長文フォームでは誤検出が多いため空を返す。
    """
    t = (text or "").strip()
    if len(t) >= HEARING_PASTE_BODY_MIN_LEN:
        return ""
    return first_http_url_in_text(t)
