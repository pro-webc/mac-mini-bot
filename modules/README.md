# `modules/` インデックス

`main.py` の `process_case` に近い順に並べています。

## 設計原則

このシステムの `modules/` は **3 つの責務** を持つ:

1. **多段 LLM チェーンの制御** — 人間の制作マニュアルを忠実にステップ分解し、各段階の出力品質を制御する
2. **全入出力の自動記録** — LLM とのやり取りを漏れなく保存し、プロンプト改善の根拠データを蓄積する
3. **品質ガードレールの実行** — プレースホルダ未置換検出、`MAX_TOKENS` 切れ警告、ビルド検証などで出力異常を即座に検知する

## オーケストレーション・入出力

| モジュール | 役割 |
|------------|------|
| `spreadsheet.py` | Google シート読み書き（AV・AW 等） |
| `case_extraction.py` | ヒアリングバンドル抽出 |
| `spec_generator.py` | ヒアリングシート取得など |

## TEXT_LLM（`llm/` サブパッケージ）

品質管理の中核。多段チェーンの制御、記録、出力検証を担う。

| モジュール | 役割 |
|------------|------|
| `llm/text_llm_stage.py` | **唯一の分岐入口**（`if/elif` → 各 `*_claude_manual` を直接呼ぶ） |
| `llm/llm_step_trace.py` | **自動記録**: `record_llm_turn` で全 Claude CLI 呼び出しの入出力を `output/` に保存 |
| `llm/llm_raw_output.py` | **正本保存**: LLM 出力を加工前の原文で保存（パーサ失敗時の切り分け用） |
| `llm/llm_pipeline_common.py` | 要望正規化・仕様組み立て・technical_spec 付与・**出力検証**（空応答・`MAX_TOKENS` 切れ） |
| `llm/basic_lp_spec.py` / `llm/basic_cp_spec.py` | BASIC LP / BASIC 向け台本・仕様ブートストラップ |
| `llm/site_script_parse.py` / `llm/spec_json_extract.py` | 台本・JSON パース |
| `llm/llm_output_files.py` | フェンス解析・パス安全性検証 |

## プラン別 Claude CLI マニュアルチェーン

各プランのチェーンは**手順ファイル** (`config/prompts/*_manual/step_*.txt`) を順に読み込み、前ステップの出力を次の入力に渡す。実行エンジンは Claude Code CLI（`claude -p`）。

| モジュール | CLI 呼び出し回数 | セッション数 |
|------------|---------|-------------|
| `basic_lp_claude_manual.py` | 11 回 | 5 タブ |
| `basic_cp_claude_manual.py` | 10 回 | 5 タブ |
| `standard_cp_claude_manual.py` | 15 回 | 6 タブ |
| `advance_cp_claude_manual.py` | 16 回 | 6 タブ |

## Manus リファクタ

| モジュール | 役割 |
|------------|------|
| `basic_lp_refactor_claude.py` | Manus 向けプロンプト組み立て（`config/prompts/manus/*.txt` から連結） |
| `manus_refactor.py` | Manus API 呼び出し・ポーリング・応答パース |

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
| `contract_workflow.py` | プラン作業分岐 |

## 関連ドキュメント

| 文書 | 内容 |
|------|------|
| **`docs/LLM_PIPELINE.md`** | 多段チェーンの設計思想・各工程の LLM 割当 |
| **`docs/OUTPUT_LAYOUT.md`** | 記録の 3 層構造（ステップトレース・チェックポイント・構造化メタ） |
| **`docs/DIRECTORY_GUIDE.md`** | リポジトリ全体の地図 |
| **`PIPELINE_TESTING.md`** | 工程テストの実行方法と検証知見 |
