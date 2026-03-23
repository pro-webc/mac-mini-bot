# `modules/` インデックス（パイプライン順）

`main.py` の `process_case` に近い順に並べています。

## オーケストレーション・入出力

| モジュール | 役割 |
|------------|------|
| `spreadsheet.py` | Google シート読み書き（AV・AW 等） |
| `case_extraction.py` | ヒアリングバンドル抽出 |
| `spec_generator.py` | ヒアリングシート取得など |

## TEXT_LLM（`llm/` サブパッケージ）

| モジュール | 分岐 / 役割 |
|------------|-------------|
| `llm/text_llm_stage.py` | TEXT_LLM 入口（`if/elif` → 各 `*_gemini_manual` を直接呼ぶ） |
| `llm/basic_lp_spec.py` / `llm/basic_cp_spec.py` | BASIC LP / BASIC 向け台本・仕様ブートストラップ |
| `llm/llm_pipeline_common.py` | 要望正規化・仕様組み立て・technical_spec 付与 |
| `llm/site_script_parse.py` / `llm/spec_json_extract.py` | 台本・JSON パース |
| `llm/llm_raw_output.py` / `llm/llm_output_files.py` | 正本保存・パス検証 |
| `basic_lp_gemini_manual.py` 等 `*_gemini_manual.py` | 実マニュアルチェーン（ルート `modules/`） |
| `basic_lp_refactor_gemini.py` | Manus 向けプロンプト組み立て |
| `manus_refactor.py` | Manus API 呼び出し |

## サイト生成・適用・ビルド

| モジュール | 役割 |
|------------|------|
| `site_generator.py` | `output/sites/<案件>/` 用意 |
| `basic_lp_generated_apply.py` | 生成マークダウン（フェンス・マーカー形式）の解析と `site_dir` への書き込み |
| `site_implementer.py` / `site_build.py` | 実装・ビルド検証 |

## デプロイ・その他

| モジュール | 役割 |
|------------|------|
| `github_client.py` | GitHub push |
| `vercel_client.py` | Vercel デプロイ |
| `gemini_site_images.py` | 画像生成（パイプライン外で呼ぶ想定の処理） |
| `contract_workflow.py` | プラン作業分岐 |

詳細は **`docs/LLM_PIPELINE.md`**、リポジトリ全体の地図は **`docs/DIRECTORY_GUIDE.md`**、工程テストは **`PIPELINE_TESTING.md`**。
