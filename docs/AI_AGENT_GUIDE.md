# AI エージェント向けシステムガイド

このドキュメントは、AI エージェント（Cursor / Claude Code 等）が **mac-mini-bot** のコードを理解・変更するための単一エントリポイントです。

## このシステムは何か

Google スプレッドシートの案件行を起点に、**ヒアリング抽出 → Claude CLI 多段チェーン（プラン別 10〜16 回）→ Manus リファクタ → Next.js ビルド → GitHub push → Vercel デプロイ**を自動実行する**半 AI ワークフローシステム**です。全 LLM 呼び出しの入出力は `output/<レコード番号>/llm_steps/` に自動保存され、人間がレビューしてプロンプトを改善するサイクルで品質を上げ続けます。

## パイプライン（5 フェーズ）

`main.py` の `WebsiteBot.process_case` が以下のメソッドを順に呼びます。

| フェーズ | メソッド | 何をするか | 主モジュール |
|----------|---------|-----------|-------------|
| 1 | `_phase1_hearing_and_branch` | スプレッドシートからヒアリング抽出 → 契約プラン → 作業分岐解決 | `case_extraction`, `contract_workflow` |
| 2 | `_phase2_text_llm` | プラン別 Claude CLI 多段チェーン（＋任意で Manus リファクタ） | `llm/text_llm_stage` → `*_claude_manual` |
| 3 | `_phase3_prepare_site` | 出力ディレクトリ生成 → LLM 生出力保存 → フェンス解析でファイル適用 | `site_generator`, `llm_raw_output`, `basic_lp_generated_apply` |
| 4 | `_phase4_build` | `npm install` + `npm run build` の検証 | `site_implementer`, `site_build` |
| 5 | `_phase5_deploy` | GitHub push → Vercel デプロイ → スプレッドシートに URL 記録 | `github_client`, `vercel_client`, `spreadsheet` |

## アーキテクチャの要点

### プラン分岐は `BRANCH_REGISTRY` で一元管理

`modules/contract_workflow.py` の `BRANCH_REGISTRY: dict[ContractWorkBranch, BranchConfig]` が全プラン（BASIC_LP / BASIC / STANDARD / ADVANCE）の設定を保持します。`text_llm_stage.run_text_llm_stage` は `BRANCH_REGISTRY` から `BranchConfig` を引き、`importlib` でパイプラインモジュールを動的にロードします。

**新プラン追加時**: `BRANCH_REGISTRY` にエントリを追加するだけで `text_llm_stage` 自体の変更は不要。

### 多段 Claude CLI チェーン

各 `*_claude_manual.py` は `config/prompts/*_manual/step_*.txt` を順に読み、前ステップの出力を `{{STEP_N_OUTPUT}}` 等のプレースホルダで次のプロンプトに注入します。実行エンジンは `claude_manual_common.py` が管理する Claude Code CLI（`claude -p` / `ClaudeCLIChat`）。

| プラン | モジュール | CLI 呼び出し回数 |
|--------|-----------|-----------------|
| BASIC LP | `basic_lp_claude_manual.py` | 11 回 |
| BASIC | `basic_cp_claude_manual.py` | 10 回 |
| STANDARD | `standard_cp_claude_manual.py` | 15 回 |
| ADVANCE | `advance_cp_claude_manual.py` | 16 回 |

### 全 LLM 入出力の自動記録

`llm_step_trace.py` の `record_llm_turn` が Claude CLI 呼び出しごとに `output/<レコード番号>/llm_steps/NNN_<種別>/` へ `input.md` / `output.md` を自動保存。失敗時は `error.txt`。Manus 呼び出しも同じ仕組みで記録。

## ディレクトリ構成（変更時に参照する場所）

```
mac-mini-bot/
├── main.py                     # エントリ・5 フェーズのオーケストレーション
├── config/
│   ├── config.py               # 環境変数・設定の Single Source of Truth
│   ├── contract_plans.py       # 契約プラン定義
│   ├── spreadsheet_schema.py   # シート列スキーマ（設定側）
│   ├── validation.py           # 起動時検証
│   └── prompts/                # プロンプト資産（テキスト編集だけで品質改善可能）
│       ├── common/             #   全プラン共通ガードレール
│       ├── *_manual/           #   プラン別 step_*.txt
│       └── manus/              #   Manus リファクタ指示
├── modules/
│   ├── contract_workflow.py    # BRANCH_REGISTRY（プラン分岐の Single Source of Truth）
│   ├── case_extraction.py      # ヒアリングバンドル抽出
│   ├── *_claude_manual.py      # プラン別 Claude CLI 多段チェーン（4 種）
│   ├── claude_manual_common.py # Claude CLI 実行基盤（全マニュアル共通）
│   ├── hearing_url_utils.py    # URL 判定・長文閾値の共有定数
│   ├── basic_lp_generated_apply.py  # フェンス解析 → site_dir へファイル適用
│   ├── site_generator.py       # 出力ディレクトリ生成
│   ├── site_build.py           # npm ビルド検証
│   ├── github_client.py        # GitHub push
│   ├── vercel_client.py        # Vercel デプロイ
│   ├── spreadsheet.py          # Google Sheets API
│   └── llm/                    # LLM 制御サブパッケージ
│       ├── text_llm_stage.py   # TEXT_LLM 入口（BRANCH_REGISTRY 駆動）
│       ├── llm_step_trace.py   # 入出力の自動記録
│       ├── llm_raw_output.py   # 正本保存
│       └── llm_pipeline_common.py  # 共通ユーティリティ・出力検証
├── scripts/                    # 工程テスト・スナップショット駆動
├── tests/                      # pytest（42 ファイル）
├── docs/                       # 本ファイルを含む設計ドキュメント
└── output/                     # 実行時の LLM 記録（git 対象外）
```

## 変更時の注意事項（必読）

### 1. 分岐修正の横展開

**ある分岐の修正を行ったら、同種の分岐を必ず確認して揃える。** 4 つの `*_claude_manual.py` は同じパターンで実装されているため、1 つを直したら残り 3 つも同じ修正が必要な可能性が高い。詳細は `.cursor/rules/parallel-branch-fixes.mdc`。

### 2. BRANCH_REGISTRY との整合

- `ContractWorkBranch` を増やしたら `BRANCH_REGISTRY` にエントリを追加
- `BranchConfig` のフィールドを変えたら全エントリを確認
- `*_claude_manual.py` のパイプライン関数シグネチャを変えたら `BranchConfig.pipeline_function` の呼び出し側（`text_llm_stage.py`）が期待する戻り値と合わせる

### 3. エラー処理の原則

- フォールバック・握りつぶしは禁止
- 失敗時は `RuntimeError` 等で明示的に例外。メッセージにモジュール名を含める
- `_subst` のプレースホルダ未置換検出は品質ガードレールの一部

### 4. YAGNI / SOLID

- 今の要件に不要な機能・引数・分岐は追加しない
- 汎用化は同一パターンが 2〜3 回現れてから
- 詳細は `.cursor/rules/solid-yagni.mdc`

### 5. コメント規約

パイプラインのフェーズ区切りや入出力が多い関数呼び出し箇所では、**引数・処理・出力** の 3 点をコメントで書く。詳細は `.cursor/rules/comment-conventions.mdc`。

## よくある変更パターン

### プロンプト品質の改善（コード変更なし）

1. `output/<レコード番号>/llm_steps/NNN_*/output.md` で品質問題を特定
2. 全プラン共通 → `config/prompts/common/technical_spec_prompt_block.txt` にルール追加
3. 特定ステップ → `config/prompts/*_manual/step_*.txt` を編集
4. `scripts/phase2_from_phase1_snapshot.py` で同じ入力に対して改善効果を検証

### 新しい契約プランの追加

1. `config/contract_plans.py` にプラン定義を追加
2. `modules/contract_workflow.py` に `ContractWorkBranch` enum 値と `BRANCH_REGISTRY` エントリを追加
3. `modules/new_plan_claude_manual.py` を作成（既存の `*_claude_manual.py` を参考に）
4. `config/prompts/new_plan_manual/step_*.txt` を作成
5. `.env` / `.env.example` に `NEW_PLAN_USE_CLAUDE_MANUAL` 等を追加

### ヒアリング解釈の変更

URL 判定・長文閾値の定数は `modules/hearing_url_utils.py` に集約されている。`fetch_hearing_sheet` / `spreadsheet_schema` / `case_extraction` がこれを参照するので、変更は 1 箇所で済む。

## 設定の起点

| 知りたいこと | 参照先 |
|-------------|--------|
| 環境変数の一覧 | `.env.example`（正本） |
| 環境変数の読み込み | `config/config.py` |
| 契約プラン定義 | `config/contract_plans.py` |
| プラン分岐の全体像 | `modules/contract_workflow.py`（`BRANCH_REGISTRY`） |
| LLM 割当の詳細 | `docs/LLM_PIPELINE.md` |
| 出力レイアウト | `docs/OUTPUT_LAYOUT.md` |
| 工程テストの方法 | `PIPELINE_TESTING.md` |
| 技術要件（ガードレール） | `config/prompts/common/technical_spec_prompt_block.txt` + `docs/TECH_REQUIREMENTS.md` |

## ドキュメント索引

| 文書 | 内容 |
|------|------|
| **`README.md`** | プロジェクト概要・クイックスタート |
| **`docs/AI_AGENT_GUIDE.md`**（本書） | AI エージェント向けシステム理解の単一エントリポイント |
| **`docs/DIRECTORY_GUIDE.md`** | リポジトリの 3 軸構成（制御・記録・改善） |
| **`docs/LLM_PIPELINE.md`** | 多段チェーンの設計思想・LLM 割当詳細 |
| **`docs/OUTPUT_LAYOUT.md`** | 多段 LLM の入出力トレース・品質問題の特定手順・トレース API |
| **`docs/TECH_REQUIREMENTS.md`** | 生成サイトの品質ガードレール |
| **`modules/README.md`** | modules/ のパイプライン順インデックス |
| **`config/prompts/README.md`** | プロンプト改善のフィードバックループ |
| **`PIPELINE_TESTING.md`** | 工程テスト・段階テストの手順 |
| **`SETUP.md`** | 認証・スプレッドシート設定 |
| **`DEPLOYMENT.md`** | 別マシンへの複製手順 |
