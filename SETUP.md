# セットアップガイド

## 前提条件

- Python 3.10 以上推奨。**venv の利用を推奨**（`README.md` の最短手順参照）
- Node.js 18 以上と **npm**（生成サイトの `npm run build`）
- Google Cloud Platform（Sheets API）・GitHub・Vercel（本番パイプライン実行時）
- **TEXT_LLM**: Claude Code CLI（マニュアル多段・サブスクリプション認証）およびプランに応じた Manus API（`docs/LLM_PIPELINE.md`）
- **Claude Code CLI**: `npm install -g @anthropic-ai/claude-code` + `claude auth login` で事前認証

## セットアップ手順

### 1. リポジトリのクローンとセットアップ

```bash
cd /path/to/mac-mini-bot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
chmod +x setup.sh scripts/*.sh
bash scripts/verify_environment.sh
```

単体テストと設定検証:

```bash
pytest
BOT_CONFIG_CHECK=1 python main.py
```

別マシンへの複製手順の一覧は **`DEPLOYMENT.md`** を参照。

起動前に設定だけ検証する場合（**.env の必須項目＋スプレッドシート1行目の列見出し**まで確認）:

```bash
BOT_CONFIG_CHECK=1 python main.py
```

### スプレッドシートの列見出し・処理順

- **1行目**の列名は `config/config.py` の `SPREADSHEET_HEADER_LABELS` に載っている列について、シートと **一致**させてください（全角半角スペースの違いは正規化して比較します）。**AV・AW（Bot ステータス列・デプロイURL列）は見出し不要**で、検証の対象外です（1行目が空でも問題ありません）。
- 上記の検証列で一致しない場合、`SPREADSHEET_HEADERS_STRICT=true`（既定）では**起動失敗**します。見出しを合わせるか、一時的に `SPREADSHEET_HEADERS_STRICT=false` で警告のみにできます。
- **処理対象**は次を満たす行です（上から順）:（1）**業務フェーズ列**（`phase_status`・既定 **M** / `overall_status`）が **`SPREADSHEET_TARGET_AI_STATUS`** と**完全一致**。（2）**AV 列**（`ai_status`）のセル値が `完了` / `処理中` / `エラー` で始まる値でない。（3）**`SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL=true`（既定）** のとき、ヒアリング列が**空**または **http(s) URL だけで構成される**行は**スキップ**（**URL 以外の本文が1文字でもある行のみ**着手）。（4）**`SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL=true`（既定）** のとき、`test_url` 列が**空**。
- Bot がスプレッドシートに**書き込む列は AV と AW のみ**です。それ以外の列は更新しません。
- **`SPREADSHEET_REQUIRED_FIELDS`**（既定: レコード番号・パートナー名・契約プラン）のいずれかが空の行は、上記を満たしても**処理しません**（ステータスも「処理中」にしません）。
- 複数件ある場合は **行番号の昇順（シートの上から）** に処理します。
- シート（タブ）名は `GOOGLE_SHEETS_SHEET_NAME`（既定 `Sheet1`）で変更できます。**スプレッドシート上の実在するタブ名と一致**させてください。存在しない名前だと `Unable to parse range` になります。

### 2. 環境変数の設定

`.env`ファイルを編集して、以下の認証情報を設定：

```bash
# Google Sheets API（詳細は本ドキュメント「3. Google Sheets API認証」）
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_SHEET_NAME=Sheet1
SPREADSHEET_HEADERS_STRICT=true
SPREADSHEET_TARGET_AI_STATUS=デモサイト制作中
SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL=true

# 要望・仕様・サイト実装テキストはモック（.env.example 参照）。実LLMはコード側で接続

# GitHub / Vercel（本番パイプライン）
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username
VERCEL_TOKEN=your_vercel_token
VERCEL_TEAM_ID=your_vercel_team_id

# 画像は Manus（nanobananaPro）が生成。Bot 側の画像 API は未使用
```

完全なキー一覧は **`.env.example`** を正とします。

### 3. Google Sheets API認証

#### 方法A: サービスアカウント JSON（既定）

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成
4. 認証情報（JSON）をダウンロード
5. `credentials/google-credentials.json`として保存
6. スプレッドシートをサービスアカウントのメールアドレスに共有

`.env` では `GOOGLE_SHEETS_AUTH_MODE=service_account`（省略時も同じ）。

#### 方法B: Application Default Credentials（JSON 鍵を使わない）

組織ポリシーで**サービスアカウント鍵の有効期限が短い**（例: 30日）場合や、鍵ファイルを置きたくない場合は、**自分の Google アカウント**で API にアクセスする方式にできます。

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) をインストール（macOS: `brew install --cask google-cloud-sdk`）
2. **Homebrew で cask が失敗する場合:** `ERROR: /usr/local/opt/python@3.13/libexec/bin/python3 does not exist` と出たら、`brew upgrade python@3.13` または `brew install python@3.13` でパスを用意してから再実行してください。
3. **Sheets 用スコープ付き**で ADC を取得する（スコープ無しの `gcloud auth application-default login` だけだと API が 403 になります）:
   - `bash scripts/gcloud_application_default_login.sh` を推奨（**cloud-platform と spreadsheets の両方**を指定）。  
   - 手動の場合は **`--scopes` に `cloud-platform` と `spreadsheets` の両方**が必要です（新版 gcloud のエラー回避）。  
   ブラウザでログイン（対象の Google アカウントはスプレッドシートの**所有者または編集権限**を持つもの）。
4. 同じ GCP プロジェクトで **Google Sheets API を有効化**（コンソールの「APIとサービス」→「ライブラリ」）
5. `.env` に次を設定:

```bash
GOOGLE_SHEETS_AUTH_MODE=application_default
# GOOGLE_SHEETS_CREDENTIALS_PATH はこのモードでは未使用（設定しても無視されないが必須ではない）
```

資格情報は通常 `~/.config/gcloud/application_default_credentials.json` に保存され、**期限付きサービスアカウント鍵ファイル**は不要です（`gcloud` の再ログインが必要になる場合はあります）。

**403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT` / `insufficient authentication scopes` のとき:** Application Default Credentials に **Sheets 用スコープ**が含まれていません。次で再ログインしてください。

```bash
bash scripts/gcloud_application_default_login.sh
# または（cloud-platform が無いと gcloud が拒否する場合があります）
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets
```

**`gcloud config get-value project` が `(unset)` のとき / 「quota project」で 403 のとき:**  
GCP 上に**プロジェクト**を用意し（[コンソール](https://console.cloud.google.com/)で作成可）、**そのプロジェクトで Google Sheets API を有効化**したうえで、次を実行します（`YOUR_PROJECT_ID` は実際の ID）。

```bash
bash scripts/gcloud_set_adc_quota_project.sh YOUR_PROJECT_ID
```

`.env` に **`GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID`** も必須です。  
プロジェクト ID は `gcloud projects list` で確認できます。

**注意:** サーバや CI では方法A（サービスアカウント＋共有）の方が向くことが多いです。Mac mini 常駐で人間と同じアカウントでよい場合は方法Bが簡単です。

### 4. GitHub認証

1. [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 「Generate new token (classic)」をクリック
3. `repo`スコープを選択
4. トークンを生成して`.env`に設定

### 5. Vercel認証

1. [Vercel Dashboard > Settings > Tokens](https://vercel.com/account/tokens)
2. トークンを生成して`.env`に設定
3. チームIDも設定（チームを使用する場合）
4. **デプロイ方式（既定）**: `VERCEL_DEPLOY_USE_GIT_SOURCE=true`（省略時も同じ）で REST API の **`gitSource`** によりデプロイします。実装は GitHub API で **`repoId`（数値）** を取得してから Vercel に渡します（`org`+`repo` だけより `incorrect_git_source_info` が出にくいです）。**`GITHUB_TOKEN`** は push に加え、この `repoId` 取得にも使います。あわせて **[Vercel GitHub App](https://github.com/apps/vercel)** を対象の org またはユーザーにインストールし、**デプロイ対象リポジトリへのアクセスを許可**してください。
5. **代替（任意）**: `VERCEL_DEPLOY_USE_GIT_SOURCE=false` にすると、GitHub API の zipball + `POST /v2/files` で **GitHub App なし**でデプロイできます（スナップショットであり、連携の扱いは gitSource 既定より弱くなりやすいです）。
6. プッシュ先ブランチが `main` でない場合は `.env` に `VERCEL_GIT_REF=ブランチ名` を設定（既定は `main`。Bot は `git push` を `main` に統一します）。

#### GitHub と Vercel を連携する（初回・人が手でやる作業）

Bot の既定デプロイ（`gitSource`）は **Vercel が GitHub のリポジトリを読めること**が前提です。次を **GitHub 側と Vercel 側**で一度セットしてください（AI はあなたのアカウントにログインできないため、ここは手作業です）。

1. **GitHub に [Vercel](https://github.com/apps/vercel) をインストール**  
   - GitHub → **Settings** → **Applications** → **Installed GitHub Apps** → **Vercel**  
   - **Configure** で、Bot が push する **ユーザー or 組織**を選び、**All repositories** または **Only select repositories** で対象リポジトリ（または org 全体）を含める。
2. **Vercel 側でも GitHub を接続**（未接続の場合）  
   - [Vercel Dashboard](https://vercel.com) → **Account Settings** → **Login Connections**（またはチームの **Settings**）で **GitHub** が接続済みか確認。  
   - 未接続なら **Connect GitHub** で OAuth し、同じ GitHub アカウントを紐づける。
3. **組織リポジトリ**の場合: GitHub の **Organization settings** → **Third-party access** / **GitHub Apps** で、Vercel がその org の repo にアクセスできるか確認（必要なら承認）。
4. 初回だけ [Vercel の New Project](https://vercel.com/new) から **Import** で同系のリポジトリを選び、ビルドが通ることを確認してもよい（API だけでも動く場合がありますが、権限トラブルの切り分けに有効です）。

**（任意）AV / AW の 1 行目に見出しを付けたいとき**（Bot 動作には不要）:

```bash
python scripts/fix_spreadsheet_headers_av_aw.py
```

### 6. Claude Code CLI のセットアップ

テキスト LLM は Claude Code CLI（サブスクリプション認証）を使用します。API キーは不要です。

```bash
npm install -g @anthropic-ai/claude-code
claude auth login   # ブラウザで Anthropic アカウントにログイン
claude auth status  # 認証済みか確認
```

## 使用方法

### 基本的な実行

```bash
chmod +x run.sh
./run.sh
```

または

```bash
python main.py
```

### パイプライン設定（サイト実装・ローカルビルド・画像の分離）

| 変数 | 説明 |
|------|------|
| `SITE_IMPLEMENTATION_ENABLED` | `true`（既定）で仕様書に基づきサイトディレクトリを用意し `npm build` を検証 |
| `SITE_BUILD_ENABLED` | `true`（既定）で `npm install` + `npm run build` をローカル検証 |
| テキスト LLM・モデル名 | `CLAUDE_*` / `MANUS_*` 等は `config/config.py` と `docs/LLM_PIPELINE.md` を参照 |

## 定期実行の設定（macOS）

macOSで定期実行するには、`launchd`を使用します：

### 1. plistファイルを作成

`~/Library/LaunchAgents/com.websitebot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.websitebot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/Yamaoka.works/propagqte/mac-mini-bot/run.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/Yamaoka.works/propagqte/mac-mini-bot</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/Yamaoka.works/propagqte/mac-mini-bot/bot.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/Yamaoka.works/propagqte/mac-mini-bot/bot.error.log</string>
</dict>
</plist>
```

### 2. launchdに登録

```bash
launchctl load ~/Library/LaunchAgents/com.websitebot.plist
```

### 3. 停止

```bash
launchctl unload ~/Library/LaunchAgents/com.websitebot.plist
```

## トラブルシューティング

### Google Sheets API認証エラー

- 認証情報ファイルのパスを確認
- サービスアカウントにスプレッドシートへのアクセス権限があるか確認

### GitHubプッシュエラー

- トークンに`repo`スコープがあるか確認
- リポジトリ名が重複していないか確認

### Vercelデプロイエラー

- トークンが有効か確認（チーム利用時は `VERCEL_TEAM_ID` も）
- 既定の gitSource デプロイ: [Vercel GitHub App](https://github.com/apps/vercel) が対象 org/user のリポジトリを参照できるか、`VERCEL_GIT_REF` が push 先ブランチと一致しているか（既定 `main`）
- `VERCEL_DEPLOY_USE_GIT_SOURCE=false`（zipball）のとき: `GITHUB_TOKEN` で zipball が取得できるか（プライベート repo は必須）

### デプロイURLが Vercel ログインを求める

- 既定ではデプロイ直後に API で **`ssoProtection`（Vercel Authentication）・パスワード保護・Trusted IPs** をプロジェクト単位で解除します（`VERCEL_FORCE_PUBLIC_DEPLOYMENTS=true`）。
- それでもログインを求める場合は **チーム全体の Deployment Protection** が優先されている可能性があります。Vercel ダッシュボードの Team Settings → Security などで確認してください。
- 自動解除をやめたい場合は `VERCEL_FORCE_PUBLIC_DEPLOYMENTS=false` にします。

## 開発・テスト

```bash
source .venv/bin/activate
pytest
ruff check main.py config/ modules/ tests/
```

## ログ

ログはプロジェクトルートの `bot.log`（UTF-8）と標準出力に出力されます。レベルは環境変数 `LOG_LEVEL`（例: `DEBUG`）で変更できます。
