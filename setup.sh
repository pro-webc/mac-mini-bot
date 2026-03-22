#!/bin/bash
# セットアップスクリプト

cd "$(dirname "$0")"

echo "Webサイト製作Botのセットアップを開始します..."

chmod +x scripts/*.sh 2>/dev/null || true

# Python仮想環境を作成
if [ ! -d ".venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv .venv
fi

# 仮想環境をアクティベート
source .venv/bin/activate

# 依存関係をインストール
echo "依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

# ディレクトリを作成
echo "ディレクトリを作成中..."
mkdir -p credentials
mkdir -p output/images
mkdir -p output/sites
mkdir -p templates

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo ".envファイルが見つかりません。.env.exampleをコピーして設定してください。"
    cp .env.example .env
    echo "編集が必要な項目:"
    echo "  - GOOGLE_SHEETS_CREDENTIALS_PATH"
    echo "  - GOOGLE_SHEETS_SPREADSHEET_ID"
    echo "  - GEMINI_API_KEY"
    echo "  - GITHUB_TOKEN"
    echo "  - VERCEL_TOKEN"
fi

echo "セットアップが完了しました！"
echo ""
echo "環境確認: bash scripts/verify_environment.sh"
echo ""
echo "次のステップ:"
echo "1. .envファイルを編集して必要な認証情報を設定"
echo "2. Google Sheets: credentials/google-credentials.json または ADC + ./scripts/gcloud_application_default_login.sh + ./scripts/gcloud_set_adc_quota_project.sh"
echo "3. bash scripts/verify_environment.sh で前提条件を確認"
echo "4. ./run.sh でBotを実行"
echo ""
echo "別PCへの移行手順は DEPLOYMENT.md を参照"
