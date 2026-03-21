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

# 画像生成のみ今回スキップ: ./run.sh --skip-images または IMAGE_GEN_SKIP_RUN=1 ./run.sh
if [ "${1:-}" = "--skip-images" ]; then
  export IMAGE_GEN_SKIP_RUN=1
  shift
fi

# Botを実行（残りの引数は python に渡す。例: ./run.sh --skip-images）
exec python main.py "$@"
