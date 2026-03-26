# `docs/` 索引

このシステムは **LLM の全入出力を記録し、プロンプトの反復改善で生成品質を上げ続ける半 AI ワークフロー**です。各ドキュメントはこの観点で整理されています。

| 文書 | 内容 |
|------|------|
| [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md) | **AI エージェント向けガイド** — システム理解の単一エントリポイント（構成・変更パターン・注意事項） |
| [DIRECTORY_GUIDE.md](./DIRECTORY_GUIDE.md) | **リポジトリの地図** — 制御する・記録する・改善するの 3 軸で構成を説明 |
| [LLM_PIPELINE.md](./LLM_PIPELINE.md) | **多段チェーンの設計思想** — なぜステップ分解するか、品質制御の仕組み、各工程の LLM 割当 |
| [OUTPUT_LAYOUT.md](./OUTPUT_LAYOUT.md) | **多段 LLM の入出力トレース** — ステップ番号とパイプラインの対応・品質問題の特定手順・トレース API・記録の 3 層構造 |
| [TECH_REQUIREMENTS.md](./TECH_REQUIREMENTS.md) | **品質ガードレール** — 過去の品質問題から蒸留されたルール集と運用サイクル |
| [../PIPELINE_TESTING.md](../PIPELINE_TESTING.md) | **工程テスト** — スナップショットによる A/B 検証・コマンド早見・検証知見 |
