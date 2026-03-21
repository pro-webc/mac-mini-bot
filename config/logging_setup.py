"""ロギングの一元設定（UTF-8・レベル・フォーマット）"""
from __future__ import annotations

import logging
import sys

from config.config import LOG_LEVEL, PROJECT_ROOT


def configure_logging() -> None:
    """
    アプリケーション全体の logging を設定する。
    basicConfig(force=True) で二重初期化を防ぐ。
    """
    level_name = (LOG_LEVEL or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_file = PROJECT_ROOT / "bot.log"
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root.addHandler(file_handler)
    root.addHandler(stream_handler)
