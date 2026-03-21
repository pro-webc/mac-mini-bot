# セットアップガイド

## 前提条件

- Python 3.10以上推奨（3.9 以上）。**仮想環境（venv）の利用を推奨**（PEP 668 対応 OS では必須に近い）
- Node.js 18以上（Next.jsサイト生成用）
- **Cursor CLI（`agent`）** … `TEXT_LLM_PROVIDER=cursor_agent_cli` のとき必須。`bash scripts/install_cursor_cli.sh` または `INSTALL_CURSOR_CLI=1 ./setup.sh`。`~/.local/bin` を PATH に追加
- Google Cloud Platformアカウント
- GitHubアカウント
- Vercelアカウント
- 画像で Gemini を使う場合は **Gemini API キー**。DALL-E を使う場合は **OpenAI API キー**。テキストは **Cursor / Claude Code CLI**（`CURSOR_AGENT_COMMAND` 等）のみ

## セットアップ手順

### 1. リポジトリのクローンとセットアップ

```bash
cd /path/to/mac-mini-bot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
chmod +x setup.sh scripts/*.sh
# Cursor CLI も入れる（テキスト LLM を agent にする場合）
INSTALL_CURSOR_CLI=1 ./setup.sh
# または ./setup.sh のあと: bash scripts/install_cursor_cli.sh
bash scripts/verify_environment.sh
```

別マシンへの複製手順の一覧は **`DEPLOYMENT.md`** を参照。

起動前に設定だけ検証する場合（**.env の必須項目＋スプレッドシート1行目の列見出し**まで確認）:

```bash
BOT_CONFIG_CHECK=1 python main.py
```

### スプレッドシートの列見出し・処理順

- **1行目**の列名は `config/config.py` の `SPREADSHEET_HEADER_LABELS` と **一致**させてください（全角半角スペースの違いは正規化して比較します）。
- 一致しない場合、`SPREADSHEET_HEADERS_STRICT=true`（既定）では**起動失敗**します。見出しを合わせるか、一時的に `SPREADSHEET_HEADERS_STRICT=false` で警告のみにできます。
- **処理対象**は次を満たす行です（上から順）:（1）**業務フェーズ列**（`phase_status`・既定 **M** / `overall_status`）が **`SPREADSHEET_TARGET_AI_STATUS`** と**完全一致**。（2）**mac-mini 列**（既定 **AV**・1行目の見出しは `mac-mini`）が `完了` / `処理中` / `エラー` で始まる値でない。（3）**`SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL=true`（既定）** のとき、ヒアリング列が**空**または**先頭が http(s) の URL だけ**の行は**スキップ**（**本文がセルに入っている行のみ**着手）。（4）**`SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL=true`（既定）** のとき、`test_url` 列が**空**。
- Bot がスプレッドシートに**書き込む列は AV（mac-mini）と AW（デプロイURL）のみ**です。それ以外の列は更新しません。
- **`SPREADSHEET_REQUIRED_FIELDS`**（既定: レコード番号・パートナー名・契約プラン）のいずれかが空の行は、上記を満たしても**処理しません**（ステータスも「処理中」にしません）。
- 複数件ある場合は **行番号の昇順（シートの上から）** に処理します。
- シート（タブ）名は `GOOGLE_SHEETS_SHEET_NAME`（既定 `Sheet1`）で変更できます。**スプレッドシート上の実在するタブ名と一致**させてください。存在しない名前だと `Unable to parse range` になります。

### 2. 環境変数の設定

`.env`ファイルを編集して、以下の認証情報を設定：

```bash
# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/google-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_SHEET_NAME=Sheet1
SPREADSHEET_HEADERS_STRICT=true
SPREADSHEET_TARGET_AI_STATUS=デモサイト制作中
SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL=true

# テキスト LLM（要望抽出・仕様書・サイト実装）— Cursor / Claude Code CLI のみ
TEXT_LLM_PROVIDER=cursor_agent_cli
# CURSOR_API_KEY=  # またはターミナルで agent login
OPENAI_API_KEY=your_openai_api_key
# GEMINI_API_KEY は画像生成（IMAGE_GEN_PROVIDER=gemini）のみ
GEMINI_API_KEY=your_gemini_api_key

# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# Vercel
VERCEL_TOKEN=your_vercel_token
VERCEL_TEAM_ID=your_vercel_team_id
```

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

**列見出し（AV / AW）を config どおりに直す**（`SPREADSHEET_HEADERS_STRICT=true` のとき）:

```bash
python scripts/fix_spreadsheet_headers_av_aw.py
```

### 6. Gemini APIキーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
2. `.env`に設定

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

### 画像生成スキルの使用

```bash
python -m skills.image_generation.skill "モダンな企業のヒーロー画像を生成" -o output/images/hero.png
```

### パイプライン設定（サイト実装・ローカルビルド・画像の分離）

| 変数 | 説明 |
|------|------|
| `SITE_IMPLEMENTATION_ENABLED` | `true`（既定）で仕様書から LLM が TSX を生成。`false` なら土台スタブのまま |
| `SITE_BUILD_ENABLED` | `true`（既定）で `npm install` + `npm run build` をローカル検証 |
| `SITE_BUILD_MAX_FIX_ATTEMPTS` | ビルド失敗時の LLM 修正リトライ回数（既定 3） |
| `TEXT_LLM_PROVIDER` | `cursor_agent_cli`（既定）または `claude_code_cli`。空なら `CURSOR_AGENT_COMMAND` 優先で cursor |
| `CLAUDE_CODE_COMMAND` / `CURSOR_AGENT_COMMAND` | プロンプトを標準入力で渡すコマンド（例: `bash scripts/cursor_agent_stdio.sh`） |
| `CURSOR_API_KEY` | Cursor CLI 用（任意。`agent login` の代わり） |
| `CURSOR_AGENT_MODEL` | 任意。指定時のみ `agent --model` に渡す。**未指定ならアカウント既定**（有料プランで Named モデルを使う場合は未指定か `gpt-5.2` 等を明示） |

**画像だけ Gemini・テキストは Cursor CLI** にする例:

1. [Cursor CLI](https://cursor.com/docs/cli/overview) を入れ、`agent` がターミナルで叩けることを確認する。  
2. `.env` で `TEXT_LLM_PROVIDER=cursor_agent_cli`、`CURSOR_AGENT_COMMAND=bash scripts/cursor_agent_stdio.sh`（リポジトリ付属。作業ディレクトリはプロジェクトルート推奨）。  
3. `IMAGE_GEN_PROVIDER=gemini`、`IMAGE_GEN_ENABLED=true`、`GEMINI_API_KEY` を設定。専用キーが無い場合は `IMAGE_GEN_ALLOW_FALLBACK_TO_MAIN_KEYS=true` で `GEMINI_API_KEY` にフォールバック。

**画像**は仕様書・サイト実装 LLM と**別の API キー**を推奨（`IMAGE_GEN_API_KEY`）。メインキーにフォールバックする場合のみ `IMAGE_GEN_ALLOW_FALLBACK_TO_MAIN_KEYS=true`。

| 変数 | 説明 |
|------|------|
| `IMAGE_GEN_ENABLED` | `true` でサイト実装**後**に画像パイプライン実行 |
| `IMAGE_GEN_PROVIDER` | `openai`（DALL-E 3） / `gemini` / `pillow`（PIL のみ） |
| `IMAGE_GEN_MODE` | `from_placeholder_source`（TSX の ImagePlaceholder 走査）または `standalone_spec`（仕様書の image_requirements のみ） |
| `IMAGE_GEN_AFTER_SITE` | `true`（既定）で実装完了後にのみ画像生成 |

生成物: `public/images/generated/*.png` と `docs/generated_images.json`。画風の一貫用に `docs/visual_style_brief.json`（実装直前に自動出力）を参照します。

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

### 画像生成エラー

- `IMAGE_GEN_PROVIDER=openai` のときは `IMAGE_GEN_API_KEY`（またはフォールバック許可時は `OPENAI_API_KEY`）を確認
- `gemini` のときは画像 API 用キーを確認（Gemini が画像バイナリを返さない場合は PIL プレースホルダにフォールバック）
- `pillow` のみなら外部 API は不要（開発用）

## 開発・テスト

```bash
source .venv/bin/activate
pytest
ruff check config modules skills tests main.py
```

## ログ

ログはプロジェクトルートの `bot.log`（UTF-8）と標準出力に出力されます。レベルは環境変数 `LOG_LEVEL`（例: `DEBUG`）で変更できます。
