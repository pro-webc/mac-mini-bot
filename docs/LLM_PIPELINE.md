# どの工程がどの LLM か（mac-mini-bot）

`main.py` の `WebsiteBot.process_case` を基準に、**外部モデル API を呼ぶ箇所**と **API を呼ばない前処理・組み立て** を分けて示す。

---

## 一覧（処理順）

| 順 | 工程（ログのイメージ） | 使うもの | 主モジュール | 有効条件・備考 |
|----|------------------------|----------|--------------|----------------|
| 1 | ヒアリング抽出 | **LLM なし** | `modules.case_extraction` | スプレッドシート／URL 取得のみ |
| 2 | TEXT_LLM（仕様・台本） | **Gemini（マニュアル手順）** | `modules.llm.text_llm_stage` → 下表 | 各 `*_USE_GEMINI_MANUAL` と `GEMINI_API_KEY` が必須 |
| 3 | 出力先ディレクトリ準備 | **LLM なし** | `modules.site_generator` | テンプレコピーなし。`TECH_REQUIREMENTS.md` のみ |
| 4 | `llm_raw_output/` 保存 | **LLM なし**（書き出しのみ） | `modules.llm.llm_raw_output` | 手順 2 の結果をファイル化 |
| 5 | 生成マークダウン → `app/` 等へ反映 | **LLM なし**（パーサ） | `modules.basic_lp_generated_apply` | フェンス優先、0 件ならマーカー形式を試す。それでも 0 件かつ `manus_deploy_github_url` があれば `main` が shallow clone |
| 6 | `npm build` 検証 | **LLM なし** | `modules.site_implementer` / `modules.site_build` | **stub 自動生成・自動パッチ・画像 TSX 置換は行わない**。ビルド失敗時もソースの自動修正はしない |
| 7 | `git push` | **LLM なし** | `modules.github_client` | |
| 8 | Vercel デプロイ | **LLM なし** | `modules.vercel_client` | 常に実行（公開 URL をスプレッドシートに記録） |

---

## TEXT_LLM（手順 2）の内訳 — 契約プラン分岐

本番は `main.process_case` が `modules.llm.text_llm_stage.run_text_llm_stage` を呼び出す。プラン分岐は `text_llm_stage` 内の `if/elif` のみ。

| 作業分岐 | 条件 | 実体 | 環境変数（Gemini 側） |
|----------|------|------|------------------------|
| BASIC LP | `ContractWorkBranch.BASIC_LP` | `run_text_llm_stage` → `run_basic_lp_gemini_manual_pipeline` | `BASIC_LP_USE_GEMINI_MANUAL=true` かつ `GEMINI_API_KEY`。未設定時は `RuntimeError` |
| BASIC（CP 1P） | `BASIC` | `run_text_llm_stage` → `run_basic_cp_gemini_manual_pipeline` | `BASIC_CP_USE_GEMINI_MANUAL=true` かつ `GEMINI_API_KEY`。未設定時は `RuntimeError` |
| STANDARD | `STANDARD` | `run_text_llm_stage` → `run_standard_cp_gemini_manual_pipeline` | `STANDARD_CP_USE_GEMINI_MANUAL=true` かつ `GEMINI_API_KEY`。未設定時は `RuntimeError` |
| ADVANCE | `ADVANCE` | `run_text_llm_stage` → `run_advance_cp_gemini_manual_pipeline` | `ADVANCE_CP_USE_GEMINI_MANUAL=true` かつ `GEMINI_API_KEY`。未設定時は `RuntimeError` |
| その他 | 上記以外 | （なし） | `run_text_llm_stage` が `RuntimeError`（`if/elif` を追加して対応） |

**タブ②（各プランの「手順1-2」と「手順1-3」）** は手作業マニュアルに合わせ、**2つのプロンプト本文を連結した1メッセージ**として `send_message` する（中間の「読み込みだけ」の応答は保存しない）。BASIC LP だけ 1-3 ファイル名が `step_1_3_nonrecruit.txt`。

### Gemini マニュアルチェーンのあとに続く「最終リファクタ」（Manus）

各 `*_cp_gemini_manual` / `basic_lp_gemini_manual` の末尾付近で、設定が有効なとき **Manus API でタスクを 1 件**作成し、ポーリングして完了まで待つ。

- **モジュール**: `modules.basic_lp_refactor_gemini.run_basic_lp_refactor_stage` → 内部で `modules.manus_refactor.run_manus_refactor_stage`
- **API**: `POST {MANUS_API_BASE}/v1/tasks`、ヘッダ `API_KEY`（`.env` の `MANUS_API_KEY`）。`MANUS_AGENT_PROFILE`（既定 `manus-1.6`）などは `config.config` を参照。GitHub 操作のため **`connectors` に公式の GitHub コネクタ UUID を付与**する（既定: 1 件。`MANUS_TASK_CONNECTORS` でカンマ区切り上書き、**空文字で `connectors` 省略**）。コネクタの OAuth は [Manus ドキュメント](https://open.manus.im/docs/connectors) のとおり **manus.im 上で事前連携**が必須。
- **マニュアル本編**: 引き続き Gemini（`GenerativeModel`、プラン別 `GEMINI_BASIC_LP_MODEL` / …）
- **ON/OFF**: `BASIC_LP_REFACTOR_AFTER_MANUAL` / `BASIC_CP_REFACTOR_AFTER_MANUAL` / `STANDARD_CP_REFACTOR_AFTER_MANUAL` / `ADVANCE_CP_REFACTOR_AFTER_MANUAL`（プランごと）
- **画像**: Manus 向けプロンプト（`config/prompts/manus/` のオーケストレーション＋リファクタ指示）により、**リファクタ成果で** `ImagePlaceholder` をやめ **`next/image` + `public/images/`（主に SVG フェンス）** に置き換える。`main` からの一括画像 API は呼ばない。

→ **テキストの多段生成は Gemini。最終リファクタは Manus（別 API キー）**。

### 手作業フローに合わせる（Manus が GitHub push → Vercel に Git URL）

`MANUS_PROVIDES_DEPLOY_GITHUB_URL` は **既定で true**。リファクタ用プロンプトに **GitHub へ push したうえで** 返答最終行を `BOT_DEPLOY_GITHUB_URL: https://github.com/...` とする指示が付く。ボットはその URL をパースして **ローカルからの `git push` をスキップ**し、`main.process_case` が `VercelClient.deploy_from_github` にその URL と、URL から解釈した **GitHub 上の repo 名**（`test-run-…` など）をプロジェクト名として渡して Vercel デプロイする。`false` にすると従来どおりボットがローカルから push してから同 API でデプロイ。push 先のヒントは任意で `MANUS_DEPLOY_GITHUB_REPO_HINT=owner/repo`。URL 行が無い場合は警告のうえ従来どおりボットが push（Vercel プロジェクト名は `sanitize_github_repo_name`）。

### Manus API プロンプト（手作業マニュアルと同一構成）

`modules.basic_lp_refactor_gemini.build_basic_lp_refactor_user_prompt` は次をこの順で連結する（プラン別の `preface_intro` は **使わない**）。本文は手作業用 `manus/*.txt` のみ（プレースホルダ展開）に揃える。

1. `config/prompts/manus/orchestration_prompt.txt` — 手作業のオーケストレーション（Repo 作成・リファクタ・nanobanana・build・push）。`{{MANUS_REPO_NAME}}` を `test-run-レコード番号`（GitHub 向け正規化）、`{{MANUS_REPO_DESCRIPTION}}` をパートナー名のみに展開。レコード番号・パートナー名は `main` の案件メタから `run_text_llm_stage` 経由で各 Gemini マニュアルに渡る。
2. 区切り `---`
3. `config/prompts/manus/refactoring_instruction_handwork.txt` — 手作業のリファクタリング指示書本文。
4. `===== BEGIN_CANVAS_SOURCE =====` … Gemini Canvas 単一ファイル … `END_CANVAS_SOURCE`

`MANUS_PROVIDES_DEPLOY_GITHUB_URL=true`（既定）のときはさらに末尾へ `config/prompts/manus/bot_deploy_instruction.txt`（＋任意で `bot_deploy_repo_hint_line.txt` と `MANUS_DEPLOY_GITHUB_REPO_HINT`）を連結する（手作業マニュアルには無い API 用。`false` で無効化可）。**GitHub トークンやパスワードは Manus に渡さない**（認証は Manus の GitHub コネクタ側）。

---

## サイト用画像（`main` では実行しない）

- **モジュール**: `modules.gemini_site_images`（`materialize_site_images`）。プレースホルダを実画像に置換する処理は **本パイプラインからは呼ばない**（成果物を勝手に書き換えないため）。必要なら別スクリプトや手元で実行。
- **API**: Google AI `generateContent`（**REST `v1beta`**）。**モデル**: `GEMINI_SITE_IMAGE_MODEL`（`config` / `.env`）

---

## このリポジトリで「LLM を使っていない」主なもの

- スプレッドシート読み書き（`modules.spreadsheet`）
- フェンス解析・ファイル適用（`basic_lp_generated_apply`）
- GitHub / Vercel の HTTP API
- `modules.llm.llm_pipeline_common` のサイト台本組み立て・パース（**生成モデル API は呼ばない**。Gemini マニュアル後の `spec` 整形などに使用）

---

## モデル名の設定（参照用）

| 用途 | 設定例（`config/config.py` / `.env`） |
|------|----------------------------------------|
| BASIC LP マニュアル本体 | `GEMINI_BASIC_LP_MODEL` |
| BASIC-CP マニュアル | `GEMINI_BASIC_CP_MODEL`（未設定時は LP と同じ） |
| STANDARD-CP マニュアル | `GEMINI_STANDARD_CP_MODEL` |
| ADVANCE-CP マニュアル | `GEMINI_ADVANCE_CP_MODEL` |
| サイト用画像（REST） | `GEMINI_SITE_IMAGE_MODEL` |

詳細なプロンプトファイルの場所は `config/prompts/README.md` を参照。
