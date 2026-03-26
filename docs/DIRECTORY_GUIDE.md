# リポジトリの見方

このシステムは **LLM の全入出力を記録し、プロンプトの反復改善で生成品質を上げ続ける半 AI ワークフロー**です。リポジトリの構成は以下の 3 つの軸で理解すると迷いにくいです:

1. **制御する** — `modules/` と `main.py` が多段 LLM チェーンを実行
2. **記録する** — `output/` に全 LLM 入出力を自動保存
3. **改善する** — `config/prompts/` のテキストを編集してプロンプトを改善

## 開発ルール（設計原則・AI 向け）

- **SOLID / YAGNI（YANGI 表記ゆれ含む）**: `.cursor/rules/solid-yagni.mdc`
- **分岐修正の横展開**: `.cursor/rules/parallel-branch-fixes.mdc`

人間・エージェントとも、上記を前提に変更する。

## 工程 → コード・成果物

| 順 | 工程（ログのイメージ） | 主な場所 |
|----|------------------------|----------|
| 1 | スプレッドシート読込・必須列チェック | `modules/spreadsheet.py`, `config/config.py`（列定義） |
| 2 | ヒアリング抽出 | `modules/case_extraction.py`, `modules/spec_generator.py`（シート取得） |
| 3 | TEXT_LLM（プラン別・フェーズ2） | `modules/llm/text_llm_stage.py`（`if/elif` → 各 `*_claude_manual.py`） |
| 3a | **各 LLM 呼び出しごとの入出力**（TEXT_LLM / Manus） | `modules/llm/llm_step_trace.py` → `output/<レコード番号>/llm_steps/<NNN>_<種別>/`（`input.md`・`output.md` 等）。**`output/sites/` より先**にここへ都度増える |
| 4 | 出力先ディレクトリ準備 | `modules/site_generator.py` → `output/sites/<案件名>/` |
| 5 | LLM 正本の保存 | `modules/llm/llm_raw_output.py` → 同一案件の `llm_raw_output/` |
| 6 | 生成マークダウン → サイトファイル反映 | `modules/basic_lp_generated_apply.py` |
| 7 | npm build | `modules/site_implementer.py`, `modules/site_build.py` |
| 8 | GitHub push → Vercel | `modules/github_client.py`, `modules/vercel_client.py` |

TEXT_LLM だけをフェーズ1成果物から再実行する場合は **`scripts/phase2_from_phase1_snapshot.py`**（`phase2_snapshots/` に保存）。

工程テストと同じ run 配下に段階的な TEXT_LLM（Claude Code CLI）試験を残す場合は、**`scripts/standard_cp_step1_from_phase1.py`** から **`standard_cp_step10_from_phase1.py`**（10/15・タブ⑤・手順5）まで（`step7` は本番の手順7-1とは別）。出力は **`claude_step_tests/<UTC>/`**。

詳細な LLM 割当は **`docs/LLM_PIPELINE.md`**。

## ルート直下（3 つの軸で分類）

```
mac-mini-bot/
│
│ ── 制御する ──────────────────────────────────
├── main.py                   # エントリ・案件ループ
├── modules/                  # パイプライン実装（一覧は modules/README.md）
│   └── llm/                  #   LLM チェーン制御・トレース・正本保存
│
│ ── 改善する ──────────────────────────────────
├── config/
│   ├── config.py             #   環境変数・列定義・プラン情報
│   └── prompts/              #   ← プロンプト改善はここを編集
│       ├── common/           #     全プラン共通ガードレール
│       ├── *_manual/         #     プラン別ステップファイル
│       └── manus/            #     Manus リファクタ指示
│
│ ── 記録する ──────────────────────────────────
├── output/                   # ← 自己改善の根拠データ（git 対象外）
│   ├── <レコード番号>/       #   案件別 llm_steps/（全入出力）
│   ├── phase2_*/             #   チェックポイント・スナップショット
│   └── sites/                #   デプロイ対象サイト
│
│ ── その他 ────────────────────────────────────
├── docs/                     # 本ファイル・LLM_PIPELINE 等
├── scripts/                  # 工程テスト・スナップショット用
├── tests/                    # pytest（41 ファイル）
├── .env / .env.example       # 環境変数（実キーは git 対象外）
└── run.sh / setup.sh         # 実行用ショートカット
```

## `config/` の見方（プロンプト改善の起点）

| パス | 役割 | 改善時に編集するか |
|------|------|--------------------|
| `config/config.py` | 環境変数・スプレッドシート列・OUTPUT_DIR 等 | まれ（API キー・モデル変更時） |
| `config/validation.py` | 起動時チェック | まれ |
| `config/prompts/common/technical_spec_prompt_block.txt` | **全プラン共通の品質ガードレール** | **頻繁**（品質問題発見時にルール追加） |
| `config/prompts/*_manual/step_*.txt` | **プラン別 TEXT_LLM マニュアルのステップファイル**（実行は Claude Code CLI） | **頻繁**（特定ステップの品質改善時） |
| `config/prompts/manus/` | **Manus リファクタ指示** | リファクタ品質の改善時 |
| `config/prompts/*_refactor/` | ログ用パス（中身の .txt は読まない） | 触らない |

`config/prompts/README.md` にフィードバックループと読み方の詳細があります。

## `modules/` の見方

工程別のインデックスは **`modules/README.md`** を参照（ファイル数が多いので、そこからジャンプする想定）。

## 実行時の `output/`（自己改善の根拠データ・git 対象外）

`output/` はこのシステムの核心部分であり、**全 LLM 入出力の記録**が蓄積される。

- **第 1 層（ステップトレース）**: `output/<レコード番号>/llm_steps/001_claude_cli_generate/` や `…_claude_cli_chat/` … と、**1 回の TEXT_LLM（Claude Code CLI）呼び出し＝1 サブフォルダ**が自動で増える。`input.md`（送ったプロンプト）と `output.md`（LLM の応答）のペア。失敗時は `error.txt`
- **第 2 層（チェックポイント）**: `output/phase2_llm_checkpoints/` に TEXT_LLM 完了分を退避、`output/phase2_complete/` にフェーズ 2 直後の正本を保存
- **第 3 層（構造化メタ）**: `spec.yaml`、`requirements_result.yaml`、`00_checkpoint.json` など機械可読なメタデータ

**品質改善の手順**: 特定案件の `llm_steps/` を開き、問題のあるステップの `input.md`（プロンプト）と `output.md`（応答）を比較して、`config/prompts/` のどのファイルを改善すべきかを判断する。

詳細は **`docs/OUTPUT_LAYOUT.md`**（記録の 3 層構造）。工程テストは **`PIPELINE_TESTING.md`**（リポジトリ直下）。
