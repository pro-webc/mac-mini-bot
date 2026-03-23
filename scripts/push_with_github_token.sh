#!/usr/bin/env bash
# 非対話で GitHub に push する（Cursor / CI 向け）
#
# 使い方:
#   export GH_TOKEN=ghp_xxxxxxxx        # classic: repo スコープ / fine-grained: Contents: Read and write
#   ./scripts/push_with_github_token.sh [branch]
#
# GH_TOKEN が空のとき、リポジトリ直下の .env から GITHUB_TOKEN= を読む（bot 用トークンと共用可）。
#
# 注意: トークンをシェル履歴に残さない。終わったら unset GH_TOKEN
set -euo pipefail
REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_PATH"
BRANCH="${1:-main}"

_load_github_token_from_dotenv() {
  local envf="$REPO_PATH/.env"
  [[ -f "$envf" ]] || return 1
  local line raw
  line="$(grep -E '^[[:space:]]*GITHUB_TOKEN=' "$envf" | tail -n1)" || return 1
  raw="${line#*=}"
  raw="${raw%$'\r'}"
  raw="${raw#\"}"
  raw="${raw%\"}"
  raw="${raw#\'}"
  raw="${raw%\'}"
  [[ -n "$raw" ]] || return 1
  export GH_TOKEN="$raw"
}

if [[ -z "${GH_TOKEN:-}" ]]; then
  if _load_github_token_from_dotenv; then
    echo "Using GITHUB_TOKEN from .env"
  else
    echo "ERROR: GH_TOKEN 未設定かつ .env に GITHUB_TOKEN がありません。" >&2
    exit 1
  fi
fi
# remote は PAT 埋め込みの一時 URL（process 内のみ）
ORIGIN_URL="$(git remote get-url origin)"
GITHUB_HOST_PATH=""
if [[ "$ORIGIN_URL" == https://github.com/* ]]; then
  GITHUB_HOST_PATH="${ORIGIN_URL#https://github.com/}"
elif [[ "$ORIGIN_URL" == git@github.com:* ]]; then
  GITHUB_HOST_PATH="${ORIGIN_URL#git@github.com:}"
else
  echo "ERROR: origin が github.com の https または SSH 形式ではありません: $ORIGIN_URL" >&2
  exit 1
fi
if [[ -z "$GITHUB_HOST_PATH" ]]; then
  echo "ERROR: origin から owner/repo を解釈できません: $ORIGIN_URL" >&2
  exit 1
fi
PUSH_URL="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_HOST_PATH}"
echo "Pushing $BRANCH to GitHub (token auth)…"
git push "$PUSH_URL" "$BRANCH"
echo "Done."
