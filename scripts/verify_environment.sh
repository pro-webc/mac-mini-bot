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

echo "=== mac-mini-bot 環境チェック (${ROOT}) ==="
echo ""

# プロジェクトの .venv を最優先（macOS 既定の python3 は 3.9 のことがある）
PY=
if [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
  echo "[OK] Python（.venv）: $PY"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
  echo "[OK] Python 3（PATH）: $PY"
else
  echo "[NG] Python 3 も .venv/bin/python も見つかりません"
  ok=1
fi

if [ -n "${PY}" ]; then
  pyver=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  echo "     バージョン: $($PY --version 2>&1)"
  if "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    :
  else
    echo "[WARN] Python 3.10 以上を推奨します（現在 ${pyver}）"
    warn=1
  fi
fi

if [ -x "$ROOT/.venv/bin/pip" ]; then
  echo "[OK] pip（.venv）: $ROOT/.venv/bin/pip"
elif command -v pip >/dev/null 2>&1; then
  echo "[OK] pip（PATH）: $(command -v pip)"
elif command -v python3 >/dev/null 2>&1 && python3 -m pip --version >/dev/null 2>&1; then
  echo "[OK] pip（python3 -m pip）"
else
  echo "[NG] pip が見つかりません: .venv を作り直すか python3 -m pip install -r requirements.txt"
  ok=1
fi
check_cmd "Node.js（npm / Next ビルド用）" "node" "https://nodejs.org/"
check_cmd "npm" "npm" "Node に同梱"

# Cursor CLI: PATH に無くても ~/.local/bin にある場合
if command -v agent >/dev/null 2>&1; then
  echo "[OK] Cursor CLI (agent): $(command -v agent)"
  agent --version 2>/dev/null || true
  echo "     --- agent whoami ---"
  agent whoami 2>/dev/null | sed 's/^/     /' || echo "     (whoami 失敗)"
  echo "     注: agent -p（本 bot の TEXT_LLM）は IDE とは別枠の利用上限になることがあります"
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
