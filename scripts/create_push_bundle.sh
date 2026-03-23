#!/usr/bin/env bash
# origin/main より先にあるローカルコミットを 1 ファイルにまとめる（権限のある別マシンへ持ち運び）
#
# 使い方:
#   ./scripts/create_push_bundle.sh [出力.bundle]
#
# 受け取り側（push できるマシン）:
#   git pull /path/to/mac-mini-bot-ahead.bundle main
#   git push origin main
set -euo pipefail
REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_PATH"
OUT="${1:-$REPO_PATH/mac-mini-bot-ahead.bundle}"
git fetch origin main 2>/dev/null || true
git bundle create "$OUT" origin/main..HEAD
echo "作成: $OUT"
echo "サイズ: $(ls -lh "$OUT" | awk '{print $5}')"
echo ""
echo "別環境で clone 済みリポに取り込む例:"
echo "  git pull $(basename "$OUT") main"
echo "  git push origin main"
