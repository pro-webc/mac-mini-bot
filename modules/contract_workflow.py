"""スプレッドシートの契約プラン（plan_type 列）に応じた作業分岐の解決。

TEXT_LLM のプロンプトチェーン・サイト実装・将来のプラン別処理の分岐先として使う。
"""
from __future__ import annotations

from enum import Enum

from config.config import get_contract_plan_info


class ContractWorkBranch(str, Enum):
    """契約プランに対応する作業パイプライン種別。"""

    BASIC_LP = "basic_lp"
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCE = "advance"


def resolve_contract_work_branch(contract_plan: str) -> ContractWorkBranch:
    """
    契約プラン列の値から作業分岐を解決する。

    シート上の表記ゆれ（大文字小文字など）は ``get_contract_plan_info`` に合わせて正規化される。
    未定義のプラン名は STANDARD 相当の情報にフォールバックしたうえで ``STANDARD`` 分岐となる。
    """
    info = get_contract_plan_info((contract_plan or "").strip())
    if info.get("type") == "landing_page":
        return ContractWorkBranch.BASIC_LP
    name = (info.get("name") or "").strip().upper()
    pages = int(info.get("pages") or 1)
    if name == "BASIC" and pages == 1:
        return ContractWorkBranch.BASIC
    if name == "ADVANCE":
        return ContractWorkBranch.ADVANCE
    if name == "STANDARD":
        return ContractWorkBranch.STANDARD
    return ContractWorkBranch.STANDARD
