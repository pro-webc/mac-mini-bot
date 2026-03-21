#!/usr/bin/env bash
# Cursor CLI（agent）を公式インストーラで入れる。
# バイナリは ~/.local/share/cursor-agent/ に展開され、~/.local/bin/agent に symlink されます。
# PATH に ~/.local/bin が無い場合は、インストール完了メッセージに従って zshrc 等へ追加してください。
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Cursor CLI 公式インストーラを実行します（要ネットワーク）..."
curl -fsS https://cursor.com/install | bash

echo ""
if command -v agent >/dev/null 2>&1; then
  echo "==> OK: agent が PATH で見つかりました"
  agent --version 2>/dev/null || true
else
  echo "==> 注意: まだ agent が PATH にありません。次を実行してからターミナルを開き直してください:"
  echo '    export PATH="$HOME/.local/bin:$PATH"'
  echo "    （恒久化: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc）"
fi
