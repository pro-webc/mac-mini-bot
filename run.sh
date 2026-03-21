#!/bin/bash
# Webサイト製作Bot実行スクリプト

cd "$(dirname "$0")"

# Cursor CLI（公式インストーラは ~/.local/bin/agent に配置）
export PATH="$HOME/.local/bin:$PATH"

# 仮想環境をアクティベート（存在する場合）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Pythonパスを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Botを実行
python main.py
