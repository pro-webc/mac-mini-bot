"""ターミナル向けログの色・記号・バナー（ファイルログには使わない）"""
from __future__ import annotations

import os
from typing import Any


# https://no-color.org/
def stream_supports_color(stream: Any) -> bool:
    if os.getenv("NO_COLOR", "").strip():
        return False
    if os.getenv("FORCE_COLOR", "").strip().lower() in ("1", "true", "yes"):
        return True
    try:
        return bool(stream.isatty())
    except (AttributeError, OSError):
        return False


# 24-bit 風の落ち着いたパレット（端末が 256 色未満でも概ね破綻しにくい）
class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def abbrev_logger_name(name: str) -> str:
    if name == "__main__":
        return "bot"
    for prefix in ("modules.", "config."):
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


def case_start_banner(
    *,
    row: Any,
    record: Any,
    partner: Any,
    use_color: bool,
) -> str:
    """案件処理開始時の複数行バナー（logger.info に1本で渡す）"""
    mode = "抽出 → TEXT_LLM → ソース push"
    partner_s = str(partner or "").strip() or "（未設定）"
    rec_s = str(record or "").strip() or "—"
    row_s = str(row if row is not None else "—")

    bar = "─" * 52
    if use_color:
        a, r = C.CYAN + C.BOLD, C.RESET
        return "\n".join(
            [
                "",
                f"  {a}╭{bar}╮{r}",
                f"  {a}│{r} 案件 #{rec_s}  ·  {partner_s[:44]}",
                f"  {a}│{r} row {row_s}  ·  {mode}",
                f"  {a}╰{bar}╯{r}",
                "",
            ]
        )
    return "\n".join(
        [
            "",
            f"  ╭{bar}╮",
            f"  │ 案件 #{rec_s}  ·  {partner_s[:44]}",
            f"  │ row {row_s}  ·  {mode}",
            f"  ╰{bar}╯",
            "",
        ]
    )


def startup_title(*, use_color: bool) -> str:
    msg = "Bot 起動 — スプレッドシートから未処理案件を読み込みます"
    if use_color:
        return f"{C.BOLD}{C.WHITE}{msg}{C.RESET}"
    return msg


def idle_banner(*, use_color: bool) -> str:
    if use_color:
        return f"{C.DIM}… 処理対象の案件はありません。スプレッドシートを待機中{C.RESET}"
    return "… 処理対象の案件はありません。スプレッドシートを待機中"


def batch_start_banner(*, count: int, max_cases: int | None, use_color: bool) -> str:
    if max_cases and max_cases > 0:
        tail = f"（先頭 {count} 件 · BOT_MAX_CASES={max_cases}）"
    else:
        tail = ""
    msg = f"▶ {count} 件の案件を順に処理します {tail}".strip()
    if use_color:
        return f"{C.BOLD}{C.GREEN}{msg}{C.RESET}"
    return msg


def all_done_banner(*, use_color: bool) -> str:
    msg = "✓ すべての案件の処理が完了しました"
    if use_color:
        return f"{C.BOLD}{C.GREEN}{msg}{C.RESET}"
    return msg
