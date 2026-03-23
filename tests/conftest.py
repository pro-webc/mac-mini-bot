"""pytest 用フック（他モジュール import より先に環境を立てる）"""
from __future__ import annotations

import os

# logging_setup が bot.log に混ざらないよう、テストセッション全体で有効にする
os.environ.setdefault("MAC_MINI_BOT_PYTEST", "1")
