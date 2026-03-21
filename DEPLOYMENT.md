# 別PC・本番マシンへのデプロイ手順

リポジトリを新しい Mac / Linux に置くときのチェックリストです。

## 1. 必須（ランタイム）

| 項目 | 用途 |
|------|------|
| **Python 3.10+** | ボット本体（`requirements.txt`） |
| **Node.js 18+** と **npm** | 生成サイトの `npm ci` / `npm run build` |
| **git** | テンプレ・出力の想定に依存する場合 |

## 2. Python 仮想環境と依存パッケージ

```bash
cd /path/to/mac-mini-bot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

`requirements.txt` … 本番実行に必要な PyPI パッケージ（Sheets / LLM API / GitHub / Vercel / 画像 等）。  
`requirements-dev.txt` … テスト・Lint（任意だが CI では両方入れる想定）。

## 3. Cursor CLI（`TEXT_LLM_PROVIDER=cursor_agent_cli` のとき）

テキスト LLM を Cursor の `agent` に任せる構成の場合:

```bash
bash scripts/install_cursor_cli.sh
# ~/.local/bin が PATH に無い場合
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
agent --version
```

手動でも可: [Cursor CLI 概要](https://cursor.com/docs/cli/overview) の `curl https://cursor.com/install | bash` と同じ内容です。

## 4. 設定ファイル

- `.env` … **別マシンでは `.env.example` をコピーして再編集**（API キー・スプレッドシート ID はその環境用）。
- Google 認証 … `credentials/`（サービスアカウント）または `application_default` + **`bash scripts/gcloud_application_default_login.sh`**（Sheets スコープ付き必須）。

## 5. 動作確認

```bash
source .venv/bin/activate
bash scripts/verify_environment.sh
BOT_CONFIG_CHECK=1 python main.py
```

## 6. 定期実行（例: launchd）

`SETUP.md` の「定期実行の設定」を参照。実行ユーザーは **PATH に `~/.local/bin`（agent）と `node` / `npm`** が通るようにしてください。
