# Webサイト受諾製作業務自動化Bot

mac miniで常時稼働するWebサイト製作自動化システム

## エラー処理の原則（必須）

- **正常ルート以外でのフォールバックは禁止**する。LLM・API・JSON パース等が失敗したときに、別経路で「とりあえず成功」させない（例: 空の既定仕様で続行、意図しないデフォルトデータで埋める、静かにスキップする）。
- 失敗時は **`RuntimeError` 等で明示的に例外**とし、メッセージに **どのモジュール・どの処理か**が分かる文言を含める（例: `modules.requirement_extractor.extract_requirements` / `modules.spec_generator.generate_spec`）。
- **理由**: フォールバックを許すと、本番で **どこで失敗したか追跡できなくなり**、原因調査が不能になるため。

## 機能

1. **スプレッドシート連携**: Google Sheetsから案件情報を取得
2. **要望抽出（TEXT_LLM 第1段）**: ヒアリング・アポメモ・営業メモから **顧客の事実・要望のみ**を JSON 化（技術仕様は含めない）
3. **仕様書生成（TEXT_LLM 第2段）**: 第1段の結果・ヒアリング・契約に **共通技術ルール**を当てはめ、実装可能な仕様 JSON を生成
4. **サイト土台**: Next.js 技術スケルトンのみ生成（`SKELETON.md`）
5. **サイト実装（LLM）**: 仕様書に基づきページ・セクションを生成し、`npm run build` 検証＋自動修正
6. **画像生成（任意・分離）**: `openai` / `gemini` / **`cursor_agent_cli`（Cursor CLI・要望と同じコマンド）** / `pillow`。プレースホルダー走査または仕様書ベースで `public/images/generated/` に出力
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
- 画像: `IMAGE_GEN_PROVIDER=gemini` のとき `GEMINI_API_KEY`（または専用 `IMAGE_GEN_API_KEY`）／`cursor_agent_cli` のときはテキスト LLM と同じ `CURSOR_AGENT_COMMAND`（応答は PNG の base64 を JSON で返す契約・失敗時は PIL プレースホルダ）
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

- **画像生成だけ今回スキップ**（`.env` の `IMAGE_GEN_ENABLED` は変えない）: `IMAGE_GEN_SKIP_RUN=1 python main.py` または `python main.py --skip-images` または `./run.sh --skip-images`

## プロジェクト構造

```
mac-mini-bot/
├── main.py                 # メインオーケストレーション
├── config/
│   ├── __init__.py
│   ├── config.py          # 設定管理（環境変数・パス等）
│   ├── prompts/           # 各工程サブフォルダ配下の *.yaml をマージ（例: prompts/image_generation/）
│   └── prompt_settings.py # 上記の読み込み・{placeholder} 差し込み
├── modules/
│   ├── __init__.py
│   ├── spreadsheet.py     # スプレッドシート連携
│   ├── requirement_extractor.py  # 第1段・要望抽出（顧客要望のみ）と検証
│   ├── spec_generator.py  # 第2段・仕様書生成（技術ルール込み）・ヒアリング取得
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
│   ├── verify_environment.sh   # 前提条件チェック（.venv / agent whoami 含む）
│   └── run_all_local_checks.sh # 環境 + pytest + 設定検証 +（任意）TEXT_LLM スモーク
├── DEPLOYMENT.md         # 別PC・本番向け手順
├── SETUP.md              # 詳細なセットアップガイド
└── README.md
```

## 処理フロー

1. **スプレッドシートから案件取得**: 起動時に**列見出し整合性チェック**のうえ、`AI統合ステータス` が設定した**フェーズ**（既定: `デモサイト制作中`）かつ**テストサイトURLが空**（既定）などの条件を満たし、**必須列がすべて入力済み**の行だけを**上から（行番号昇順）**取得
2. **要望抽出**: **TEXT_LLM 第1段**で `requirements_result`（顧客要望のみ。技術ルールは含めない）
3. **仕様書生成**: **TEXT_LLM 第2段**で `spec`（`get_common_technical_spec` 等のルールに沿い、**ルートページ数は契約プランの `pages` に固定**）
4. **サイト土台生成**: Next.js 技術スケルトンのみ出力
5. **サイト実装**: LLM が TSX を生成 → `npm run build` が通るまで修正（`SITE_IMPLEMENTATION_ENABLED`）
6. **画像生成（任意）**: サイト実装**後**、別キーで実行（`IMAGE_GEN_ENABLED`）。`docs/visual_style_brief.json` で画風を共有
7. **GitHubプッシュ**: 新規リポジトリ名は `レコード番号-パートナー名`（英数字・ハイフンに正規化）で作成してプッシュ
8. **Vercelデプロイ**: 既定は `gitSource`（Vercel GitHub App 連携）。必要なら `VERCEL_DEPLOY_USE_GIT_SOURCE=false` で zipball アップロード
9. **URL確認**: デプロイURLが閲覧可能か確認
10. **スプレッドシート更新**: デプロイURLを最終列に記録

環境変数の一覧は `.env.example` を参照。

### mac-mini（AV）列が「エラー: …」になるとき

本番で例外が出ると `エラー: ` に続けて **例外メッセージ**が書かれます（プレフライト実行時はシートを更新しません）。

- **要望抽出**で始まる場合（第1段）: TEXT_LLM（`CURSOR_AGENT_COMMAND` / `CLAUDE_CODE_COMMAND`）の **失敗・タイムアウト・空応答**、または **JSON パース失敗**、`plan_type` 不一致、`client_voice` / `facts` 不正など。詳細は **`bot.log`** と `TEXT_LLM_CLI_TIMEOUT_SEC` を確認。
- **usage limit / Cursor Pro** と出る場合: **無料プランに落ちたとは限らない**（有料でも CLI のエージェント枠・月次上限で同様の文言になり得る）。**`agent whoami` でメール一致 → `agent logout` / `agent login` → [Cursor ダッシュボード](https://cursor.com) の Usage/Billing** の順で確認。**手順の詳細は `SETUP.md` の「Cursor CLI が usage limit…」**。切替: `.env` で **`TEXT_LLM_PROVIDER=claude_code_cli`** と **`CLAUDE_CODE_COMMAND`**。
- **仕様書生成**で始まる場合（第2段）: 第2段 LLM 失敗・`site_overview` 欠落など。
- 表示が途中で切れる場合は `SPREADSHEET_AI_STATUS_ERROR_MAX_LEN`（既定 200）を増やす。

### テスト実行（本番と同じ案件取得・push/デプロイのみ省略）

- **一括（推奨）**: `bash scripts/run_all_local_checks.sh` — 環境チェック → `pytest` → `BOT_CONFIG_CHECK=1 main.py` → 既定で **要望+仕様スモーク**（Cursor `agent -p` が2回・利用上限に当たり得る）。スモークだけ省略する場合は `SKIP_TEXT_LLM_SMOKE=1 bash scripts/run_all_local_checks.sh`
- **要望抽出（第1段）+ 仕様書（第2段）のスモーク**: `python scripts/run_extraction_and_spec_smoke.py`（結果は `output/smoke/`）
- **本番と同じスプレッドシートから案件取得 → 各工程どおり処理し、Git push・Vercel デプロイ・スプレッドシートのデプロイ URL / 完了列（AV・AW）の更新だけ行わない**:  
  `python scripts/run_preflight_before_push.py`  
  - **既定**: 本番と同じ **`get_pending_cases()`** で1件選び `WebsiteBot.process_case` を実行（上から何件目かは `PREFLIGHT_SHEET_CASE_INDEX`、特定行は `PREFLIGHT_SHEET_ROW_NUMBER`）。  
  - **各工程の出力**は `output/preflight/test-{レコード番号}-{パートナー名}/` に保存（`preflight_full.json` 等）。再実行のたびにそのフォルダは作り直し。  
  - `SpreadsheetClient` は本番と同様に常に使う（`.env` の Sheets 認証が必要）。起動検証は `main.py` と同様 **`require_full_pipeline=true`**（GitHub / Vercel トークンも確認対象）。  
  - **擬似1行だけ試す場合（本番と異なる）**: `PREFLIGHT_SOURCE=env` と `PREFLIGHT_HEARING_SHEET_URL` 等（`.env.example` 参照）。
