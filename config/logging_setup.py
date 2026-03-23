"""ロギングの一元設定（UTF-8・レベル・フォーマット）"""
from __future__ import annotations

import logging
import os
import sys
import time
from typing import ClassVar

from config.config import LOG_LEVEL, PROJECT_ROOT
from config.log_theme import C, abbrev_logger_name, stream_supports_color


class PrettyStreamFormatter(logging.Formatter):
    """
    標準出力向け: 時刻・レベル・モジュールを短く整え、TTY のときだけ色付けする。
    """

    _LEVEL_META: ClassVar[dict[int, tuple[str, str, str]]] = {
        logging.DEBUG: (C.GRAY, "DBG", "·"),
        logging.INFO: (C.CYAN, "INFO", "◆"),
        logging.WARNING: (C.YELLOW, "WARN", "⚠"),
        logging.ERROR: (C.RED, "ERR ", "✖"),
        logging.CRITICAL: (C.MAGENTA + C.BOLD, "CRIT", "‼"),
    }

    def __init__(self, *, use_color: bool) -> None:
        super().__init__()
        self._use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 — ログフォーマッタの堅牢性
            message = str(record.msg)

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        ct = time.localtime(record.created)
        t = time.strftime("%H:%M:%S", ct)
        name = abbrev_logger_name(record.name)
        if len(name) > 18:
            name = name[:17] + "…"

        if self._use_color:
            color, lvl_label, sym = self._LEVEL_META.get(
                record.levelno, (C.WHITE, record.levelname[:4].upper(), "·")
            )
            dim = C.DIM
            reset = C.RESET
            meta = (
                f"{dim}{t}{reset} "
                f"{color}{sym}{reset} "
                f"{color}{lvl_label:4}{reset} "
                f"{dim}{name:18}{reset}"
            )
        else:
            _, lvl_label, sym = self._LEVEL_META.get(
                record.levelno, (C.WHITE, record.levelname[:4].upper(), "·")
            )
            meta = f"{t} {sym} {lvl_label:4} {name:18}"

        if message.startswith("\n"):
            head = meta + message
        else:
            head = meta + " " + message

        if record.exc_text:
            return head + "\n" + record.exc_text
        return head


def configure_logging() -> None:
    """
    アプリケーション全体の logging を設定する。
    basicConfig(force=True) で二重初期化を防ぐ。
    """
    level_name = (LOG_LEVEL or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # テスト実行時は本番 bot.log と分離（pytest が先に conftest を読むこと）
    _pytest_mode = os.environ.get("MAC_MINI_BOT_PYTEST", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    log_file = (
        PROJECT_ROOT / "bot-test.log" if _pytest_mode else PROJECT_ROOT / "bot.log"
    )
    file_fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(file_fmt, datefmt=datefmt))

    use_color = stream_supports_color(sys.stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(PrettyStreamFormatter(use_color=use_color))

    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    # サードパーティの「エラーに見える INFO」を抑える（Sheets 起動時の file_cache 等）
    for name in (
        "googleapiclient.discovery_cache",
        "google.auth.transport.requests",
        "urllib3",
        "urllib3.connectionpool",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
