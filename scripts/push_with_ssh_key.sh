#!/usr/bin/env bash
# 指定した秘密鍵だけで push（複数 GitHub アカウントの切り分け用）
#
# 使い方:
#   ./scripts/push_with_ssh_key.sh ~/.ssh/id_ed25519_pro_webc [branch]
#
# pro-webc 用の鍵が「書き込み権限のある GitHub アカウント」に紐づいている必要があります。
set -euo pipefail
REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_PATH"
KEY_FILE="${1:?秘密鍵のパスを第1引数で指定してください}"
BRANCH="${2:-main}"
if [[ ! -f "$KEY_FILE" ]]; then
  echo "ERROR: 鍵ファイルがありません: $KEY_FILE" >&2
  exit 1
fi
if [[ "$KEY_FILE" = /* ]]; then
  KEY_ABS="$KEY_FILE"
else
  KEY_ABS="$(cd "$(dirname "$KEY_FILE")" && pwd)/$(basename "$KEY_FILE")"
fi
export GIT_SSH_COMMAND="ssh -i ${KEY_ABS} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
REMOTE="${MAC_MINI_BOT_SSH_REMOTE:-git@github.com:pro-webc/mac-mini-bot.git}"
echo "Pushing $BRANCH via $KEY_FILE → $REMOTE"
git push "$REMOTE" "$BRANCH"
echo "Done."
