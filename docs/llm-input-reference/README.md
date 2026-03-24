# LLM プロンプトから抽出したルール索引

本フォルダは、`config/prompts/` 配下の複数プロンプト（Gemini 向け `*_manual/*.txt` / Manus 向け `manus/*.txt` / 共通 `common/*.txt`）に散在するルール・指示を抽出・整理したものです。

実装フローの詳細は `docs/LLM_PIPELINE.md` を参照してください。

## 統合ファイル

**[all-rules.md](./all-rules.md)** — 全ルールを 1 ファイルにまとめたもの。

1. ランタイム入力（プレースホルダ・チェーン出力）
2. サイト構成ルール
3. デザインルール（配色・レイアウト・UI 品質）
4. 技術要件（スタック・実装制約）
5. コンテンツ・コピー・表現
6. Git / リポジトリ / デプロイ連携

## 個別ファイル（参考）

| ファイル | 領域 |
|----------|------|
| [runtime-inputs.md](./runtime-inputs.md) | ランタイム入力 |
| [site-structure-rules.md](./site-structure-rules.md) | サイト構成 |
| [design-rules.md](./design-rules.md) | デザイン |
| [technical-requirements.md](./technical-requirements.md) | 技術要件 |
| [git-and-deploy-rules.md](./git-and-deploy-rules.md) | Git / デプロイ |
| [content-and-expression.md](./content-and-expression.md) | コンテンツ・表現 |
