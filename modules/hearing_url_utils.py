"""ヒアリング列（AH）の本文・URL 解釈を `spec_generator` / マニュアル / スキーマで共有する。

参考サイト URL の抽出は LLM 工程（``claude_manual_common.run_reference_url_extraction``）に
移行済み。本モジュールにはフェッチ前段の閾値定数・既存サイト推定・デザイン関連行抽出が残る。
"""
from __future__ import annotations

import re
from collections.abc import Sequence

# ``fetch_hearing_sheet`` と同一閾値（長文＝コピペ本文とみなす）
HEARING_PASTE_BODY_MIN_LEN = 400

# ``spec_generator.fetch_hearing_sheet`` の文中 URL 検出と整合
HEARING_HTTP_URL_RE = re.compile(r"https?://[^\s\]<>\")]+", re.IGNORECASE)


def first_http_url_in_text(text: str) -> str:
    """文中の最初の http(s) URL（末尾の句読点のみ除去）。"""
    m = HEARING_HTTP_URL_RE.search(text or "")
    return m.group(0).rstrip(".,;") if m else ""


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


def hearing_reference_design_excerpt(
    text: str,
    *,
    extra_texts: Sequence[str] = (),
    max_chars: int = 4500,
) -> str:
    """
    ヒアリング全文から、参考サイト・デザイン・雰囲気に関係しそうな行を拾い、
    前後1行の文脈付きで連結する（長文コピペでも下流に渡しやすいよう短くする）。

    *extra_texts* にアポメモ・営業メモ等を渡すと、デザイン関連行として追加される。
    キーワード行が無いときは先頭から ``max_chars`` までを返す。
    """
    combined = (text or "").strip()
    extra_design_lines: list[str] = []
    for et in extra_texts:
        s = (et or "").strip()
        if not s:
            continue
        for line in s.splitlines():
            if _REF_LINE_HINT_RE.search(line):
                extra_design_lines.append(line)

    t = combined
    if not t:
        if extra_design_lines:
            return "\n".join(extra_design_lines).strip()[:max_chars]
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
        if extra_design_lines:
            merged.append("")
            merged.append("【営業メモ・アポメモからのデザイン関連情報】")
            merged.extend(extra_design_lines)
        out = "\n".join(merged).strip()
        if len(out) > max_chars:
            return out[: max_chars - 12].rstrip() + "\n…（以降省略）"
        return out
    result = t
    if extra_design_lines:
        result += "\n\n【営業メモ・アポメモからのデザイン関連情報】\n"
        result += "\n".join(extra_design_lines)
    if len(result) <= max_chars:
        return result
    return result[: max_chars - 12].rstrip() + "\n…（以降省略）"


# 電話・住所・料金・スケジュール・口コミ等（コード生成・ファクトチェック用の再掲）
_FACTUAL_LINE_HINT_RE = re.compile(
    r"(電話|TEL|tel:|メール|e-?mail|mail|@|住所|所在地|番地|丁目|号室|"
    r"\d+階|階建|"
    r"営業時間|定休|"
    r"料金|プラン|円|入会|体験|キャンペーン|特典|割引|"
    r"スケジュール|時間割|曜日|[月火水木金土日]曜|"
    r"口コミ|評価|レビュー|お客様の声|"
    r"プロフィール|経歴|資格|モットー|担当|講師|スタッフ|代表|"
    r"LINE|Instagram|Facebook|Twitter|SNS|"
    r"CTA|優先|問い合わせ方法|連絡先|"
    r"090\d|080\d|070\d|"
    r"https?://)",
    re.IGNORECASE,
)


def hearing_factual_data_excerpt(
    text: str,
    *,
    extra_texts: Sequence[str] = (),
    max_chars: int = 6000,
) -> str:
    """
    ヒアリング全文から、連絡先・料金・スケジュール・口コミ等の事実行を拾い、
    前後1行の文脈付きで連結する（手順7のファクトチェック用）。

    *extra_texts* にアポメモ・営業メモ等を渡すと、該当行として追加される。
    マッチが無いときは ``hearing_reference_design_excerpt`` と同様に先頭から切り詰める。
    """
    combined = (text or "").strip()
    extra_factual_lines: list[str] = []
    for et in extra_texts:
        s = (et or "").strip()
        if not s:
            continue
        for line in s.splitlines():
            if _FACTUAL_LINE_HINT_RE.search(line):
                extra_factual_lines.append(line)

    t = combined
    if not t:
        if extra_factual_lines:
            return "\n".join(extra_factual_lines).strip()[:max_chars]
        return ""
    lines = t.splitlines()
    picked: set[int] = set()
    for i, line in enumerate(lines):
        if _FACTUAL_LINE_HINT_RE.search(line):
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
        if extra_factual_lines:
            merged.append("")
            merged.append("【営業メモ・アポメモからの事実情報】")
            merged.extend(extra_factual_lines)
        out = "\n".join(merged).strip()
        if len(out) > max_chars:
            return out[: max_chars - 12].rstrip() + "\n…（以降省略）"
        return out
    result = t
    if extra_factual_lines:
        result += "\n\n【営業メモ・アポメモからの事実情報】\n"
        result += "\n".join(extra_factual_lines)
    if len(result) <= max_chars:
        return result
    return result[: max_chars - 12].rstrip() + "\n…（以降省略）"


def hearing_factual_data_block_for_prompt(
    text: str,
    *,
    extra_texts: Sequence[str] = (),
    max_chars: int = 6000,
) -> str:
    """
    手順7-2 / 7-3 や結合ログ向けに、そのまま差し込める事実情報ブロック文字列。
    """
    t = (text or "").strip()
    has_extra = any((et or "").strip() for et in extra_texts)
    if not t and not has_extra:
        return (
            "（ヒアリング原文の事実情報再掲なし。手順1-3 とサイト構成の【テキスト情報】を参照すること。）"
        )
    body = hearing_factual_data_excerpt(t, extra_texts=extra_texts, max_chars=max_chars)
    if not body:
        return (
            "（ヒアリング原文の事実情報再掲なし。手順1-3 とサイト構成の【テキスト情報】を参照すること。）"
        )
    return (
        "【ヒアリング原文・事実データ（電話・住所・料金・スケジュール・口コミ等。欠落禁止）】\n"
        + body
    )


def hearing_reference_design_block_for_prompt(
    text: str,
    *,
    extra_texts: Sequence[str] = (),
    max_chars: int = 4500,
) -> str:
    """
    マニュアル手順6・7-1 や Manus 向けに、そのまま差し込めるブロック文字列。

    *extra_texts* にアポメモ・営業メモ等を渡すと、デザイン関連情報を追加で含める。
    ヒアリング本文が空のときは「再掲なし」の一文のみ（プレースホルダ未置換を防ぐ）。
    """
    t = (text or "").strip()
    has_extra = any((et or "").strip() for et in extra_texts)
    if not t and not has_extra:
        return "（ヒアリング原文の再掲なし。手順1-3 と手順4 の出力を参照すること。）"
    body = hearing_reference_design_excerpt(t, extra_texts=extra_texts, max_chars=max_chars)
    if not body:
        return "（ヒアリング原文の再掲なし。手順1-3 と手順4 の出力を参照すること。）"
    return (
        "【ヒアリング原文・参考サイト・デザイン関連（下流でも必ず反映すること）】\n"
        + body
    )
