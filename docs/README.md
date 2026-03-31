# `docs/` 索引

このシステムは **LLM の全入出力を記録し、プロンプトの反復改善で生成品質を上げ続ける半 AI ワークフロー**です。各ドキュメントはこの観点で整理されています。

| 文書 | 内容 |
|------|------|
| [AI_WORKFLOW_ARCHITECTURE.md](./AI_WORKFLOW_ARCHITECTURE.md) | **AI ワークフローアーキテクチャ** — システム全体像・3 層の役割分担・Cursor の位置づけ・進化の方向性 |
| [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md) | **AI エージェント向けガイド** — システム理解の単一エントリポイント（構成・変更パターン・注意事項） |
| [DIRECTORY_GUIDE.md](./DIRECTORY_GUIDE.md) | **リポジトリの地図** — 制御する・記録する・改善するの 3 軸で構成を説明 |
| [LLM_PIPELINE.md](./LLM_PIPELINE.md) | **多段チェーンの設計思想** — なぜステップ分解するか、品質制御の仕組み、各工程の LLM 割当 |
| [OUTPUT_LAYOUT.md](./OUTPUT_LAYOUT.md) | **多段 LLM の入出力トレース** — ステップ番号とパイプラインの対応・品質問題の特定手順・トレース API・記録の 3 層構造 |
| [TECH_REQUIREMENTS.md](./TECH_REQUIREMENTS.md) | **品質ガードレール** — 過去の品質問題から蒸留されたルール集と運用サイクル |
| [RESUME_AND_TROUBLESHOOTING.md](./RESUME_AND_TROUBLESHOOTING.md) | **再開ガイド & 障害対応表** — 再開スクリプトの選択フロー・フェーズ別の障害原因と対応 |
| [../PIPELINE_TESTING.md](../PIPELINE_TESTING.md) | **工程テスト** — スナップショットによる A/B 検証・コマンド早見・検証知見 |
| [knowledge/](./knowledge/README.md) | **運用ナレッジベース** — 実案件から得た問題分析・修正効果・プロンプト改善の記録 |

### AI ワークフロー進化計画

| 文書 | 内容 |
|------|------|
| [EVOLUTION_ROADMAP.md](./EVOLUTION_ROADMAP.md) | **進化ロードマップ** — 半 AI → 自律 AI への全体計画・フェーズ依存関係・設計原則 |
| [AUTO_SCORING.md](./AUTO_SCORING.md) | **自動スコアリング設計（Phase A）** — 技術/構造/デザイン/コンテンツの 4 軸評価・モジュール構成・出力フォーマット |
| [FEEDBACK_LOOP.md](./FEEDBACK_LOOP.md) | **フィードバックループ設計（Phase B）** — 低スコア検出→原因特定→改善提案→A/B 検証→適用のサイクル |
| [OBSERVABILITY.md](./OBSERVABILITY.md) | **可観測性設計（Phase D）** — メトリクス・構造化ログ・アラート・ダッシュボードの 4 層設計 |
