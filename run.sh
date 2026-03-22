#!/bin/bash
# Webサイト製作Bot実行スクリプト

cd "$(dirname "$0")"

# 仮想環境をアクティベート（存在する場合）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Pythonパスを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

exec python main.py "$@"
