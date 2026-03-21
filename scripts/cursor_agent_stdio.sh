#!/usr/bin/env bash
# Cursor CLI: 標準入力の全文をプロンプトとして渡し、応答を標準出力へ。
# 事前に公式インストール: https://cursor.com/docs/cli/overview
#   curl https://cursor.com/install -fsS | bash
# （既定では ~/.local/bin に agent が入る。未ログインシェルでも動くよう PATH を補う）
set -euo pipefail

# 任意: 先頭に追加したい bin（例: export CURSOR_AGENT_PATH_EXTRA=/custom/bin）
if [[ -n "${CURSOR_AGENT_PATH_EXTRA:-}" ]]; then
  export PATH="${CURSOR_AGENT_PATH_EXTRA}:${PATH}"
fi
export PATH="${HOME}/.local/bin:${HOME}/.cursor/bin:/opt/homebrew/bin:/usr/local/bin:${PATH}"

resolve_agent() {
  if [[ -n "${CURSOR_AGENT_BIN:-}" && -x "${CURSOR_AGENT_BIN}" ]]; then
    echo "${CURSOR_AGENT_BIN}"
    return 0
  fi
  if command -v agent >/dev/null 2>&1; then
    command -v agent
    return 0
  fi
  for p in \
    "${HOME}/.local/bin/agent" \
    "${HOME}/.cursor/bin/agent" \
    "/opt/homebrew/bin/agent" \
    "/usr/local/bin/agent"
  do
    if [[ -x "$p" ]]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

AGENT_BIN="$(resolve_agent)" || {
  echo "ERROR: agent が見つかりません。インストール: curl https://cursor.com/install -fsS | bash" >&2
  echo "  または CURSOR_AGENT_BIN=/path/to/agent を設定してください。" >&2
  exit 127
}

PROMPT=$(cat)
# 非対話（Bot/CI）では Workspace Trust を自動承認（初回の対話プロンプトを省略）
# モデル: CURSOR_AGENT_MODEL を .env で指定したときだけ --model に渡す（配列は macOS 既定 bash で set -u と相性が悪いため if 分岐にする）
# 未指定のときは --model なしで Cursor アカウントの既定モデルを使う
if [[ -n "${CURSOR_AGENT_MODEL:-}" ]]; then
  exec "$AGENT_BIN" --trust --model "${CURSOR_AGENT_MODEL}" -p "$PROMPT" --output-format text
else
  exec "$AGENT_BIN" --trust -p "$PROMPT" --output-format text
fi
