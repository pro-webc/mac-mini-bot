# リポジトリの見方（工程対応つき）

`main.py` の `WebsiteBot.process_case` の並びと対応させた目次です。工程ごとのテストでは **左の工程 → 右のフォルダ／モジュール** を追うと迷いにくいです。

## 開発ルール（設計原則・AI 向け）

- **SOLID / YAGNI（YANGI 表記ゆれ含む）**: `.cursor/rules/solid-yagni.mdc`
- **分岐修正の横展開**: `.cursor/rules/parallel-branch-fixes.mdc`

人間・エージェントとも、上記を前提に変更する。

## 工程 → コード・成果物

| 順 | 工程（ログのイメージ） | 主な場所 |
|----|------------------------|----------|
| 1 | スプレッドシート読込・必須列チェック | `modules/spreadsheet.py`, `config/config.py`（列定義） |
| 2 | ヒアリング抽出 | `modules/case_extraction.py`, `modules/spec_generator.py`（シート取得） |
| 3 | TEXT_LLM（プラン別・フェーズ2） | `modules/llm/text_llm_stage.py`（`if/elif` → 各 `*_gemini_manual.py`） |
| 3a | **各 LLM 呼び出しごとの入出力**（Gemini / Manus） | `modules/llm/llm_step_trace.py` → `output/<レコード番号>/llm_steps/<NNN>_<種別>/`（`input.md`・`output.md` 等）。**`output/sites/` より先**にここへ都度増える |
| 4 | 出力先ディレクトリ準備 | `modules/site_generator.py` → `output/sites/<案件名>/` |
| 5 | LLM 正本の保存 | `modules/llm/llm_raw_output.py` → 同一案件の `llm_raw_output/` |
| 6 | 生成マークダウン → サイトファイル反映 | `modules/basic_lp_generated_apply.py` |
| 7 | npm build | `modules/site_implementer.py`, `modules/site_build.py` |
| 8 | GitHub push → Vercel | `modules/github_client.py`, `modules/vercel_client.py` |

TEXT_LLM だけをフェーズ1成果物から再実行する場合は **`scripts/phase2_from_phase1_snapshot.py`**（`phase2_snapshots/` に保存）。

工程テストと同じ run 配下に段階的な Gemini 試験を残す場合は **`scripts/gemini_standard_cp_step1_from_phase1.py`**（1/15）〜**`step10_from_phase1.py`**（10/15・タブ⑤・手順5）まで（`step7` は本番の手順7-1とは別）→ `gemini_step_tests/<UTC>/`。

詳細な LLM 割当は **`docs/LLM_PIPELINE.md`**。

## ルート直下（よく触るもの）

```
mac-mini-bot/
├── main.py                 # エントリ・案件ループ
├── run.sh                  # 実行用ショートカット（あれば）
├── .env                    # 実キー（git 対象外）
├── .env.example            # 変数テンプレート
├── config/                 # 設定・列定義・プロンプト群
├── modules/                # パイプライン実装（一覧は modules/README.md）
├── docs/                   # 本ファイル・LLM_PIPELINE・TECH_REQUIREMENTS 等
├── scripts/                # gcloud / 工程テスト・検証用シェル
├── tests/                  # pytest
└── output/                 # 実行時生成（既定・git 対象外）
```

## `config/` の見方

| パス | 役割 |
|------|------|
| `config/config.py` | 環境変数・スプレッドシート列・OUTPUT_DIR 等 |
| `config/validation.py` | 起動時チェック |
| `config/prompts/common/technical_spec_prompt_block.txt` | 技術要件（UTF-8 純テキスト・仕様文に注入） |
| `config/prompts/*_manual/` | 契約プラン別 **Gemini マニュアル** ステップ（`step_*.txt`） |
| `config/prompts/manus/` | **Manus** 用（手作業マニュアル相当のテキスト） |
| `config/prompts/*_refactor/` | ログ用パス（中身の .txt は読まない）。Manus 本文は `manus/` |

`config/prompts/README.md` に YAML / マニュアルの読み方があります。

## `modules/` の見方

工程別のインデックスは **`modules/README.md`** を参照（ファイル数が多いので、そこからジャンプする想定）。

## 実行時の `output/`（git 対象外）

- **フェーズ2（TEXT_LLM）中**: `begin_case_llm_trace` で `output/<レコード番号>/llm_steps/` を用意し、**Gemini の `generate_content` が返るたび**に `001_gemini_generate_content/` … のように **1 呼び出し＝1 サブフォルダ**が増える（Manus も `record_llm_turn` で同様）。ここを見れば「LLM に渡した／返った」が追える。
- **フェーズ3以降**: 案件ごとに `output/sites/<パートナー名>-<レコード番号>/` ができます。

詳細は **`docs/OUTPUT_LAYOUT.md`**。

工程テストで `pipeline_test_runs/...` に溜めた **preflight / phase1 / work_branch / phase2 / gemini_step** の説明・コマンド・検証知見は **`PIPELINE_TESTING.md`**（リポジトリ直下）。
