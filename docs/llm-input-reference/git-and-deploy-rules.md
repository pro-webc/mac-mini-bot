# Git / リポジトリ / push・デプロイ連携ルール

派生版 **`mac-mini-bot-v2`** の **LLM 2 段**索引の一部（主に第 2 段 Manus・`BOT_DEPLOY_GITHUB_URL`）。全体は [README](./README.md) / [README](../../README.md)。

## 対象

主に **Manus 第2フェーズ**（`config/prompts/manus/*.txt`）と、`MANUS_PROVIDES_DEPLOY_GITHUB_URL` 有効時の**返答形式**。ローカルでの `modules.github_client` による push は別経路（`docs/LLM_PIPELINE.md` 参照）。

## リポジトリ作成（Manus 手順 1）

`orchestration_prompt.txt` より:

- ワークスペース: **propagate-webcreation**
- **private** のまま、テンプレート **`propagate-webcreation/DefaultSetting`**
- **リポジトリ名**: `{{MANUS_REPO_NAME}}` → 実装では `bot-{レコード番号}-{先方名}`（`modules.basic_lp_refactor_gemini.manus_repo_name_for_prompt`）。先方名はスプレッドシートの **partner_name** と同一。GitHub 規則に合わない文字は `_` / `-` に置換可。
- **Description**: `{{MANUS_REPO_DESCRIPTION}}` → `test` + 先方名（例: `test株式会社ABC`）。工程テスト・本番共通。
- **同名リポジトリが既に存在する場合は直ちに終了**。

## ビルドと push（Manus）

- `npm run build` が成功するまで修正ループ。
- 成功後に **GitHub へ push**。
- コミットメッセージ・作業ログに **装飾用 Unicode 絵文字を含めない**（`bot_deploy_instruction.txt` でも再掲）。

## `BOT_DEPLOY_GITHUB_URL`（API 連携時・既定オン）

`bot_deploy_instruction.txt`（`MANUS_PROVIDES_DEPLOY_GITHUB_URL=true` のとき `build_basic_lp_refactor_user_prompt` 末尾に連結）:

- push 完了後、返答の **最後の非空行** を次の形式の **1 行だけ**にする:  
  `BOT_DEPLOY_GITHUB_URL: https://github.com/オーナー/リポジトリ.git`
- この行の**後**に文字・空行・見出しを書かない（パーサ互換のため）。
- 報告文・サマリーは **すべてこの行より前**。フェンス付きマークダウン規則は従来どおり。
- `.git` 付き URL を推奨。

### 任意ヒント

- 環境変数 `MANUS_DEPLOY_GITHUB_REPO_HINT` が設定されているとき、`bot_deploy_repo_hint_line.txt` から 1 行が差し込まれ、推奨の `owner/repo` が示される。

## ボット側の扱い（概要）

- `MANUS_PROVIDES_DEPLOY_GITHUB_URL` が真で URL が取れた場合、**ローカルからの git push をスキップ**し、その URL を元に Vercel デプロイ等に回す流れ（詳細は `docs/LLM_PIPELINE.md` の Manus 節）。
- 偽・トークンは Manus プロンプトに含めない（GitHub コネクタで OAuth）。

## 参考ファイル

| ファイル | 役割 |
|----------|------|
| `config/prompts/manus/orchestration_prompt.txt` | リポジトリ作成〜build/push の手順全体 |
| `config/prompts/manus/bot_deploy_instruction.txt` | 返答末尾の URL 行（必須） |
| `config/prompts/manus/bot_deploy_repo_hint_line.txt` | `MANUS_DEPLOY_GITHUB_REPO_HINT` 用 1 行 |
| `config/prompts/manus/README.md` | 手作業と API の対応表 |
