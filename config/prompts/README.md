# `config/prompts/` の見方

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
