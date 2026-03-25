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


# 参考サイト・デザイン希望など「下流で再掲」する行の抽出用（単独の「サイト」は誤爆しやすいので避ける）
_REF_LINE_HINT_RE = re.compile(
    r"(参考サイト|参考URL|参考に|デザイン|配色|トーン|雰囲気|モチーフ|おしゃれ|"
    r"シンプル|モダン|クール|高級|リファレンス|ビジュアル|トンマナ|レイアウト|イメージ|"
    r"https?://|希望する[^\n]{0,40}サイト|好みの[^\n]{0,20}サイト)",
    re.IGNORECASE,
)


def hearing_reference_design_excerpt(text: str, *, max_chars: int = 4500) -> str:
    """
    ヒアリング全文から、参考サイト・デザイン・雰囲気に関係しそうな行を拾い、
    前後1行の文脈付きで連結する（長文コピペでも下流に渡しやすいよう短くする）。

    マッチが無いときは ``reference_site_url_from_hearing`` の URL 周辺、
    それも無ければ先頭から ``max_chars`` までを返す。
    """
    t = (text or "").strip()
    if not t:
        return ""
    lines = t.splitlines()
    picked: set[int] = set()
    for i, line in enumerate(lines):
        if _REF_LINE_HINT_RE.search(line):
            for j in range(max(0, i - 1), min(len(lines), i + 2)):
                picked.add(j)
    if picked:
        merged: list[str] = []
        prev: str | None = None
        for idx in sorted(picked):
            ln = lines[idx]
            if ln != prev:
                merged.append(ln)
            prev = ln
        out = "\n".join(merged).strip()
        if len(out) > max_chars:
            return out[: max_chars - 12].rstrip() + "\n…（以降省略）"
        return out
    url = reference_site_url_from_hearing(t)
    if url:
        pos = t.find(url)
        if pos >= 0:
            half = max(800, max_chars // 2)
            start = max(0, pos - half // 2)
            end = min(len(t), pos + len(url) + half)
            chunk = t[start:end].strip()
            if start > 0:
                chunk = "…\n" + chunk
            if end < len(t):
                chunk = chunk + "\n…"
            if len(chunk) > max_chars:
                return chunk[: max_chars - 12].rstrip() + "\n…（以降省略）"
            return chunk
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 12].rstrip() + "\n…（以降省略）"


def hearing_reference_design_block_for_prompt(text: str, *, max_chars: int = 4500) -> str:
    """
    マニュアル手順6・7-1 や Manus 向けに、そのまま差し込めるブロック文字列。

    ヒアリング本文が空のときは「再掲なし」の一文のみ（プレースホルダ未置換を防ぐ）。
    """
    t = (text or "").strip()
    if not t:
        return "（ヒアリング原文の再掲なし。手順1-3 と手順4 の出力を参照すること。）"
    body = hearing_reference_design_excerpt(t, max_chars=max_chars)
    return (
        "【ヒアリング原文・参考サイト・デザイン関連（下流でも必ず反映すること）】\n"
        + body
    )
