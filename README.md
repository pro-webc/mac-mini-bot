# Webサイト受諾製作業務自動化Bot

mac miniで常時稼働するWebサイト製作自動化システム

## 機能

1. **スプレッドシート連携**: Google Sheetsから案件情報を取得
2. **要望抽出**: アポ録画メモと営業共有事項から要望を抽出
3. **仕様書生成**: ヒアリングシート、要望、契約プランから仕様書を作成
4. **サイト土台**: Next.js 技術スケルトンのみ生成（`SKELETON.md`）
5. **サイト実装（LLM）**: 仕様書に基づきページ・セクションを生成し、`npm run build` 検証＋自動修正
6. **画像生成（任意・分離）**: 別 API キー推奨。プレースホルダー実装ソース走査または仕様書ベースで `public/images/generated/` に出力
7. **GitHub連携**: 新規リポジトリとしてプッシュ
8. **Vercel連携**: 自動デプロイとビルドエラー修正
9. **スプレッドシート更新**: デプロイURLを最終列に記録

## セットアップ

### 1. 依存関係（別PC・本番含む）

- **Python 3.10+**（venv 推奨）
- **Node.js 18+** と **npm**（生成サイトの `npm run build` 用）
- テキスト LLM に **Cursor CLI** を使う場合: `bash scripts/install_cursor_cli.sh`（`~/.local/bin` を PATH に）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
chmod +x setup.sh scripts/*.sh
./setup.sh
# Cursor CLI も入れる場合
INSTALL_CURSOR_CLI=1 ./setup.sh
# または後から: bash scripts/install_cursor_cli.sh
bash scripts/verify_environment.sh
```

詳細・チェックリストは **`DEPLOYMENT.md`** と **`SETUP.md`** を参照。

### 2. 環境変数の設定

`.env.example` を `.env` にコピーして編集（キーは **環境ごとに再設定**）：

- Google Sheets / GitHub / Vercel
- 画像用 `GEMINI_API_KEY`（`IMAGE_GEN_PROVIDER=gemini` 時）
- テキスト（要望・仕様・サイト実装）は **Cursor / Claude Code CLI のみ**: `TEXT_LLM_PROVIDER=cursor_agent_cli` と `CURSOR_AGENT_COMMAND=bash scripts/cursor_agent_stdio.sh`（または `claude_code_cli` + `CLAUDE_CODE_COMMAND`）

### 3. Google Sheets API認証

1. Google Cloud Consoleでプロジェクトを作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、認証情報をダウンロード
4. スプレッドシートをサービスアカウントに共有

## 使用方法

```bash
python main.py
```

## プロジェクト構造

```
mac-mini-bot/
├── main.py                 # メインオーケストレーション
├── config/
│   ├── __init__.py
│   └── config.py          # 設定管理
├── modules/
│   ├── __init__.py
│   ├── spreadsheet.py     # スプレッドシート連携
│   ├── requirement_extractor.py  # 要望抽出
│   ├── spec_generator.py  # 仕様書生成
│   ├── site_generator.py  # Next.js 技術土台のみ生成
│   ├── site_implementer.py # 仕様書ベースの LLM 実装 + ビルド修正ループ
│   ├── llm_output_files.py # LLM ファイルブロックのパース（軽量・テスト容易）
│   ├── site_build.py      # npm install / build
│   ├── image_generator.py # 分離パイプライン画像生成
│   ├── github_client.py   # GitHub連携
│   └── vercel_client.py   # Vercel連携
├── templates/
│   └── nextjs_template/   # Next.js 土台テンプレート（サイト生成時にコピー元）
├── skills/
│   └── image_generation/  # 画像生成スキル
│       ├── __init__.py
│       └── skill.py       # コマンド操作で画像生成
├── output/                # 生成されたサイトと画像の出力先
│   ├── images/
│   └── sites/
├── credentials/           # 認証情報（.gitignore対象）
├── requirements.txt      # Python依存関係
├── .env.example          # 環境変数テンプレート
├── setup.sh              # セットアップスクリプト（INSTALL_CURSOR_CLI=1 で Cursor CLI も）
├── run.sh                # 実行スクリプト
├── scripts/
│   ├── cursor_agent_stdio.sh   # Cursor agent へ stdin 渡し（TEXT_LLM 用）
│   ├── install_cursor_cli.sh   # 公式 Cursor CLI インストーラ
│   └── verify_environment.sh   # 前提条件チェック
├── DEPLOYMENT.md         # 別PC・本番向け手順
├── SETUP.md              # 詳細なセットアップガイド
└── README.md
```

## 処理フロー

1. **スプレッドシートから案件取得**: 起動時に**列見出し整合性チェック**のうえ、`AI統合ステータス` が設定した**フェーズ**（既定: `デモサイト制作中`）かつ**テストサイトURLが空**（既定）などの条件を満たし、**必須列がすべて入力済み**の行だけを**上から（行番号昇順）**取得
2. **要望抽出**: アポ録画メモと営業共有事項からLLMで要望を抽出
3. **仕様書生成**: ヒアリングシート、要望、契約プランから仕様書を生成
4. **サイト土台生成**: Next.js 技術スケルトンのみ出力
5. **サイト実装**: LLM が TSX を生成 → `npm run build` が通るまで修正（`SITE_IMPLEMENTATION_ENABLED`）
6. **画像生成（任意）**: サイト実装**後**、別キーで実行（`IMAGE_GEN_ENABLED`）。`docs/visual_style_brief.json` で画風を共有
7. **GitHubプッシュ**: 新規リポジトリ名は `レコード番号-パートナー名`（英数字・ハイフンに正規化）で作成してプッシュ
8. **Vercelデプロイ**: 既定は `gitSource`（Vercel GitHub App 連携）。必要なら `VERCEL_DEPLOY_USE_GIT_SOURCE=false` で zipball アップロード
9. **URL確認**: デプロイURLが閲覧可能か確認
10. **スプレッドシート更新**: デプロイURLを最終列に記録

環境変数の一覧は `.env.example` を参照。
