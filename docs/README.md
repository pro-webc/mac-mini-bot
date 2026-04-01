# `docs/` 索引

このシステムは **LLM の全入出力を記録し、プロンプトの反復改善で生成品質を上げ続ける半 AI ワークフロー**です。ドキュメントは次のように分けています。

- **統合CLI向け**（Cursor / Claude Code 等でリポジトリを触るとき）— システムの開発・運用・障害対応
- **工程内CLI向け**（パイプライン設計・検証）— Claude CLI / Manus がどう呼ばれるか、出力の読み方
- **生成サイトのルール** — 成果物が満たすべき技術・品質基準
- **将来計画・ナレッジ** — 自律化ロードマップと実案件からの記録

**工程で実際に渡すプロンプト本文**の正本は **[`config/prompts/`](../config/prompts/README.md)**（`common/`・`*_manual/`・`manus/`）。**Cursor が自動で読む開発ルール**は **[`.cursor/rules/`](../.cursor/rules/)**。

---

## `system-rules/` — 統合CLI向け（システムのルール・ガイド）

| 文書 | 内容 |
|------|------|
| [AI_WORKFLOW_ARCHITECTURE.md](./system-rules/AI_WORKFLOW_ARCHITECTURE.md) | **AI ワークフローアーキテクチャ** — 全体像・3 層の役割分担・Cursor の位置づけ |
| [AI_AGENT_GUIDE.md](./system-rules/AI_AGENT_GUIDE.md) | **AI エージェント向けガイド** — 単一エントリ（構成・変更パターン・注意事項） |
| [DIRECTORY_GUIDE.md](./system-rules/DIRECTORY_GUIDE.md) | **リポジトリの地図** — 制御する・記録する・改善するの 3 軸 |
| [RESUME_AND_TROUBLESHOOTING.md](./system-rules/RESUME_AND_TROUBLESHOOTING.md) | **再開 & 障害対応** — 再開スクリプト・フェーズ別の原因と対応 |

---

## `pipeline/` — 工程内CLI・パイプラインの設計と検証

| 文書 | 内容 |
|------|------|
| [LLM_PIPELINE.md](./pipeline/LLM_PIPELINE.md) | **多段チェーン** — ステップ分解の思想、各工程の LLM 割当 |
| [OUTPUT_LAYOUT.md](./pipeline/OUTPUT_LAYOUT.md) | **入出力トレース** — `llm_steps/` の構造・品質問題の追い方 |
| [PIPELINE_TESTING.md](./pipeline/PIPELINE_TESTING.md) | **工程テスト** — スナップショット A/B・コマンド早見・検証知見 |

---

## `site-rules/` — 生成サイトについてのルール

| 文書 | 内容 |
|------|------|
| [TECH_REQUIREMENTS.md](./site-rules/TECH_REQUIREMENTS.md) | **品質ガードレール** — 技術・デザイン制約と運用サイクル（LLM 注入の人間向け要約） |

---

## `roadmap/` — AI ワークフロー進化計画

| 文書 | 内容 |
|------|------|
| [EVOLUTION_ROADMAP.md](./roadmap/EVOLUTION_ROADMAP.md) | **進化ロードマップ** — 半 AI → 自律 AI |
| [AUTO_SCORING.md](./roadmap/AUTO_SCORING.md) | **自動スコアリング（Phase A）** |
| [FEEDBACK_LOOP.md](./roadmap/FEEDBACK_LOOP.md) | **フィードバックループ（Phase B）** |
| [OBSERVABILITY.md](./roadmap/OBSERVABILITY.md) | **可観測性（Phase D）** |

---

## `knowledge/` — 運用ナレッジ

| 文書 | 内容 |
|------|------|
| [knowledge/README.md](./knowledge/README.md) | **運用ナレッジベース** — 実案件の問題分析・修正効果の記録 |
