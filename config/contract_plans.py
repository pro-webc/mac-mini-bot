"""契約プラン定義と名前正規化。

``config.config`` から re-export されるため、既存の
``from config.config import get_contract_plan_info`` は変更不要。
"""
from __future__ import annotations

import re

CONTRACT_PLANS = {
    "BASIC LP": {
        "name": "BASIC LP",
        "pages": 1,
        "type": "landing_page",
    },
    "BASIC": {
        "name": "BASIC",
        "pages": 1,
        "type": "website",
    },
    "STANDARD": {
        "name": "STANDARD",
        "pages": 6,
        "type": "website",
    },
    "ADVANCE": {
        "name": "ADVANCE",
        "pages": 12,
        "type": "website",
    },
}


def _normalize_plan_name(raw: str) -> str:
    """スプレッドシートの価格接尾辞 ``(9,800円)`` 等を除去して大文字化する。

    連続空白は1つに畳む（``BASIC  LP`` と ``BASIC LP`` を同一視するため）。
    """
    s = (raw or "").strip().upper()
    paren = s.find("(")
    if paren > 0:
        s = s[:paren].rstrip()
    s = re.sub(r"\s+", " ", s.strip())
    return s


def get_contract_plan_info(plan_name: str) -> dict:
    """契約プラン情報を取得。価格接尾辞付き・表記ゆれに対応。"""
    normalized = _normalize_plan_name(plan_name)
    if normalized in ("BASICLP", "BASIC-LP"):
        normalized = "BASIC LP"

    items = sorted(
        CONTRACT_PLANS.items(),
        key=lambda kv: len(kv[0]),
        reverse=True,
    )
    for key, value in items:
        if key.upper() == normalized or value["name"].upper() == normalized:
            return value

    return CONTRACT_PLANS["STANDARD"]
