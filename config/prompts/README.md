# `config/prompts/` — プロンプトエンジニアリングの主戦場

このディレクトリは、生成サイトの品質を決定する**全プロンプト資産**を管理する。コード変更なしにテキストファイルを編集するだけで、LLM の出力品質を改善できる。

## プロンプト改善のフィードバックループ

```
output/<record>/llm_steps/NNN_*/output.md   ← 品質問題を発見
          ↓
config/prompts/ のテキストを編集            ← ルール追加・手順改善
          ↓
scripts/ で工程リプレイ                     ← 同じ入力で改善効果を検証
          ↓
git diff で差分管理                         ← プロンプトの変更履歴を追跡
```

### 改善の 2 つのレベル

| レベル | 対象ファイル | 影響範囲 | 典型的な改善 |
|--------|-------------|---------|-------------|
| **全プラン共通** | `common/technical_spec_prompt_block.txt` | 全案件・全ステップ | 「絵文字禁止」「shadow-2xl 禁止」等のガードレール追加 |
| **特定ステップ** | `*_manual/step_*.txt` | 該当プランの該当ステップのみ | 「ページ構成でセクションを薄くしない」等の手順レベルの改善 |

## 自動読み込み（共通・プレーンテキスト）

**`config/prompts/common/technical_spec_prompt_block.txt`** を UTF-8 のまま読み、  
`get_technical_spec_prompt_block()` 経由で仕様・マニュアルに注入する技術要件テキストとする。

- YAML やフロントマターは使わない。**編集はそのまま貼り付け・追記できる純テキスト**。
- プレースホルダー `{name}` を本文に書く場合の差し込みは `config/prompt_settings.py` の `format_prompt` を参照。

## ディレクトリ一覧（ざっくり）

| ディレクトリ | 内容 |
|--------------|------|
| `common/` | `technical_spec_prompt_block.txt`（技術要件・上記） |
| `basic_lp_manual/` | BASIC LP・Gemini マニュアル `step_*.txt` |
| `basic_cp_manual/` | BASIC（CP 1P）マニュアル |
| `standard_cp_manual/` | STANDARD マニュアル |
| `advance_cp_manual/` | ADVANCE マニュアル |
| `basic_lp_refactor/` 等 | プラン別ログ用パスのみ（中身の .txt は読まない）。**Manus リファクタ本文は `manus/`** |
| `manus/` | **Manus** 手作業相当プロンプト（`README.md` あり） |

契約プラン別の `*_manual/*.txt` は **各 `*_gemini_manual.py` が直接読みます**（`common/` のテキストとは自動結合されません）。

## プレースホルダ規約

| 種類 | 記法 | 用途 |
|------|------|------|
| 共通テキスト | `{name}` | `prompt_settings.format_prompt` で差し込み |
| マニュアル / Manus | `{{KEY}}` | 各 `*_gemini_manual.py` の `_subst` で置換。**未置換が残ると `RuntimeError`** |

未置換プレースホルダの検出は品質ガードレールの一部として機能する。`_subst` 関数は `{{` の残留を検知し、プロンプトの組み立てミスを即座に例外で止める。
