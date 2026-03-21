#!/usr/bin/env bash
# ローカルで一括検証: 環境 → pytest → 設定検証 →（任意）TEXT_LLM スモーク
#   bash scripts/run_all_local_checks.sh
# Cursor の agent -p が利用上限のときスモークは失敗する。省略する場合:
#   SKIP_TEXT_LLM_SMOKE=1 bash scripts/run_all_local_checks.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="${HOME}/.local/bin:${HOME}/.cursor/bin:${PATH}"

echo ">>> verify_environment.sh"
bash scripts/verify_environment.sh

echo ""
echo ">>> pytest tests/"
./.venv/bin/python -m pytest tests/ -q

echo ""
echo ">>> BOT_CONFIG_CHECK=1 main.py"
BOT_CONFIG_CHECK=1 ./.venv/bin/python main.py

if [ "${SKIP_TEXT_LLM_SMOKE:-0}" = "1" ]; then
  echo ""
  echo ">>> SKIP_TEXT_LLM_SMOKE=1 — 要望抽出+仕様スモークを省略"
else
  echo ""
  echo ">>> run_extraction_and_spec_smoke.py（Cursor CLI 2 回・利用上限に注意）"
  ./.venv/bin/python scripts/run_extraction_and_spec_smoke.py
fi

echo ""
echo "=== run_all_local_checks: すべて完了 ==="
