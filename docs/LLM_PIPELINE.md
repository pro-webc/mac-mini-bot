# どの工程がどの LLM か（mac-mini-bot）

`main.py` の `WebsiteBot.process_case` を基準に、**外部モデル API を呼ぶ箇所**と **ルールベース（モック）** を分けて示す。

---

## 一覧（処理順）

| 順 | 工程（ログのイメージ） | 使うもの | 主モジュール | 有効条件・備考 |
|----|------------------------|----------|--------------|----------------|
| 1 | ヒアリング抽出 | **LLM なし** | `modules.case_extraction` | スプレッドシート／URL 取得のみ |
| 2 | TEXT_LLM（仕様・台本） | **Gemini またはモック** | `modules.text_llm_stage` → 下表 | 契約分岐で分岐 |
| 3 | サイト土台コピー | **LLM なし** | `modules.site_generator` | テンプレ複製 |
| 4 | `llm_raw_output/` 保存 | **LLM なし**（書き出しのみ） | `modules.llm_raw_output` | 手順 2 の結果をファイル化 |
| 5 | フェンス → `app/` 反映 | **LLM なし**（パーサ） | `modules.basic_lp_generated_apply` | 常に実行（該当プランで Gemini マニュアルが有効なとき、適用 0 件なら失敗） |
| 6 | サイト用画像生成 | **Gemini（画像 API・REST）** | `modules.gemini_site_images` | `GEMINI_API_KEY` があるとき常に試行（プレースホルダが無ければ 0 件） |
| 7 | `npm build` 検証 | **LLM なし** | `modules.site_implementer` / `modules.site_build` | |
| 8 | `git push` | **LLM なし** | `modules.github_client` | |
| 9 | Vercel デプロイ | **LLM なし** | `modules.vercel_client` | 常に実行（公開 URL をスプレッドシートに記録） |

---

## TEXT_LLM（手順 2）の内訳 — 契約プラン分岐

入口は常に `modules.text_llm_stage.run_text_llm_stage`。

| 作業分岐 | 条件 | 実体 | 環境変数（Gemini 側） |
|----------|------|------|------------------------|
| BASIC LP | `ContractWorkBranch.BASIC_LP` | `run_basic_lp_text_llm_pipeline` | 既定: `BASIC_LP_USE_GEMINI_MANUAL=true`。`GEMINI_API_KEY` あり → `basic_lp_gemini_manual`。**false またはキーなしはモック** |
| BASIC（CP 1P） | `BASIC` | `run_basic_text_llm_pipeline` | 既定: `BASIC_CP_USE_GEMINI_MANUAL=true`。キーあり → `basic_cp_gemini_manual`。**false またはキーなしはモック** |
| STANDARD | `STANDARD` | `run_standard_text_llm_pipeline` | 既定: `STANDARD_CP_USE_GEMINI_MANUAL=true`。キーあり → `standard_cp_gemini_manual`。**false またはキーなしはモック** |
| ADVANCE | `ADVANCE` | `run_advance_text_llm_pipeline` | 既定: `ADVANCE_CP_USE_GEMINI_MANUAL=true`。キーあり → `advance_cp_gemini_manual`。**false またはキーなしはモック** |
| その他 | 上記以外 | `run_mock_text_llm_pipeline` | モックのみ |

### Gemini マニュアルチェーンの中に含まれる「リファクタ」

各 `*_cp_gemini_manual` / `basic_lp_gemini_manual` の末尾付近で、設定が有効なとき **追加の 1 セッション**として呼ばれる。

- **モジュール**: `modules.basic_lp_refactor_gemini.run_basic_lp_refactor_stage`
- **モデル**: マニュアル本体と同じ `GenerativeModel`（プラン別に `GEMINI_BASIC_LP_MODEL` / `GEMINI_BASIC_CP_MODEL` / … を参照）
- **ON/OFF**: `BASIC_LP_REFACTOR_AFTER_MANUAL` / `BASIC_CP_REFACTOR_AFTER_MANUAL` / `STANDARD_CP_REFACTOR_AFTER_MANUAL` / `ADVANCE_CP_REFACTOR_AFTER_MANUAL`（プランごと）

→ **テキストの多段生成 + 任意のリファクタ 1 回はすべて Google Gemini（`google.generativeai`）経由**。

---

## 画像生成（手順 6）

- **API**: Google AI の `generateContent`（**REST `v1beta`**）。SDK のマニュアルチェーンとは別経路。
- **モデル**: `GEMINI_SITE_IMAGE_MODEL`（既定は画像生成向けモデル名。`.env` で変更可）
- **コード**: `modules.gemini_site_images.generate_image_bytes`

---

## このリポジトリで「LLM を使っていない」主なもの

- スプレッドシート読み書き（`modules.spreadsheet`）
- フェンス解析・ファイル適用（`basic_lp_generated_apply`）
- GitHub / Vercel の HTTP API
- `llm_mock` 内の固定文・YAML 組み立て（**外部 API 呼び出しなし**）

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
