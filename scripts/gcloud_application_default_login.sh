#!/usr/bin/env bash
# Google Sheets（application_default）用: ブラウザでログインし ADC を ~/.config/gcloud に保存する
# 使い方: chmod +x scripts/gcloud_application_default_login.sh && ./scripts/gcloud_application_default_login.sh

set -euo pipefail
cd "$(dirname "$0")/.."

# Homebrew の google-cloud-sdk が参照する Python（python@3.13 が無いと cask インストールが失敗することがある）
if [[ -x "/usr/local/opt/python@3.13/libexec/bin/python3" ]]; then
  export CLOUDSDK_PYTHON="/usr/local/opt/python@3.13/libexec/bin/python3"
elif [[ -x "/opt/homebrew/opt/python@3.13/libexec/bin/python3" ]]; then
  export CLOUDSDK_PYTHON="/opt/homebrew/opt/python@3.13/libexec/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  export CLOUDSDK_PYTHON="$(command -v python3)"
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud が見つかりません。先に: brew install --cask google-cloud-sdk" >&2
  exit 1
fi

# ADC を取得（Sheets 用スコープ必須。新版 gcloud は --scopes 指定時に cloud-platform も必須）
# 参考: https://cloud.google.com/docs/authentication/troubleshoot-adc
SCOPES="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets"
exec gcloud auth application-default login --scopes="${SCOPES}"
