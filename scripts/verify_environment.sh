#!/usr/bin/env bash
# 実運用マシン向け: Python / Node / Cursor CLI など前提条件の確認
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$PATH"

ok=0
warn=0

check_cmd() {
  local name="$1"
  shift
  if command -v "$1" >/dev/null 2>&1; then
    echo "[OK] $name: $(command -v "$1")"
  else
    echo "[NG] $name が見つかりません: 必要なら $*"
    ok=1
  fi
}

check_ver() {
  local name="$1"
  local cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $name: $($cmd 2>/dev/null | head -1)"
  else
    echo "[NG] $name"
    ok=1
  fi
}

echo "=== mac-mini-bot 環境チェック（$ROOT）==="
echo ""

check_ver "Python 3" "python3"
if command -v python3 >/dev/null 2>&1; then
  pyver=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  echo "     バージョン: $(python3 --version)"
  # 3.10 未満は警告のみ
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    :
  else
    echo "[WARN] Python 3.10 以上を推奨します（現在 ${pyver}）"
    warn=1
  fi
fi

check_cmd "pip（venv 内推奨）" "pip" "python3 -m pip install -r requirements.txt"
check_cmd "Node.js（npm / Next ビルド用）" "node" "https://nodejs.org/"
check_cmd "npm" "npm" "Node に同梱"

# Cursor CLI: PATH に無くても ~/.local/bin にある場合
if command -v agent >/dev/null 2>&1; then
  echo "[OK] Cursor CLI (agent): $(command -v agent)"
  agent --version 2>/dev/null || true
elif [ -x "$HOME/.local/bin/agent" ]; then
  echo "[WARN] agent は ~/.local/bin にありますが PATH に通っていません"
  echo "       export PATH=\"\$HOME/.local/bin:\$PATH\""
  warn=1
else
  echo "[NG] Cursor CLI (agent): TEXT_LLM_PROVIDER=cursor_agent_cli のとき必須"
  echo "     bash scripts/install_cursor_cli.sh"
  ok=1
fi

if [ -d "$ROOT/.venv" ]; then
  echo "[OK] 仮想環境 .venv が存在します"
else
  echo "[WARN] .venv がありません。./setup.sh または: python3 -m venv .venv"
  warn=1
fi

if [ -f "$ROOT/.env" ]; then
  echo "[OK] .env が存在します"
else
  echo "[WARN] .env がありません。.env.example をコピーして編集してください"
  warn=1
fi

echo ""
if [ "$ok" -eq 0 ] && [ "$warn" -eq 0 ]; then
  echo "=== 問題なさそうです。BOT_CONFIG_CHECK=1 python main.py で設定検証できます ==="
  exit 0
fi
if [ "$ok" -ne 0 ]; then
  echo "=== 不足があります。上記を解消してから実行してください ==="
  exit 1
fi
echo "=== 警告のみです。必要に応じて対応してください ==="
exit 0
