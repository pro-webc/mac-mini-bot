#!/usr/bin/env bash
# Application Default Credentials にクォータプロジェクトを紐づける（Sheets API 403 対策）
#
# 事前に GCP でプロジェクトを作成し、Google Sheets API を有効化しておいてください。
# プロジェクト ID の確認: gcloud projects list
#
# 使い方:
#   chmod +x scripts/gcloud_set_adc_quota_project.sh
#   ./scripts/gcloud_set_adc_quota_project.sh YOUR_PROJECT_ID
#
set -euo pipefail

if [[ $# -lt 1 ]] || [[ -z "${1// }" ]]; then
  echo "使い方: $0 <GCPプロジェクトID>" >&2
  echo "例: $0 my-company-prod-123" >&2
  echo "プロジェクト一覧: gcloud projects list" >&2
  exit 1
fi

PROJECT_ID="$1"

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud が見つかりません。Google Cloud SDK をインストールしてください。" >&2
  exit 1
fi

echo "==> gcloud の既定プロジェクトを設定します: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "==> Application Default Credentials のクォータプロジェクトを設定します"
gcloud auth application-default set-quota-project "$PROJECT_ID"

echo ""
echo "OK. 次を .env に追記してください:"
echo "  GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo ""
echo "（未実施なら）Sheets API 有効化:"
echo "  gcloud services enable sheets.googleapis.com --project=$PROJECT_ID"
