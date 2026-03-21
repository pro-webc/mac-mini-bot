# プロンプト YAML（工程フォルダ）

要望・仕様の生成は **`llm_mock`** が主で、これら YAML は **将来の実 LLM 接続時**に参照されます。現状よく効くのは **共通技術要件**（`common/`）です。

```
config/prompts/
├── common/
├── requirement_extraction/
├── spec_generation/
└── site_implementation/
```

- **フォルダ名** = マージ後の第1キー（例: `site_implementation.system`）。
- **`*.yaml` が1つも無いフォルダ**（`advance_cp_manual` などマニュアル用 `*.txt` のみ）は `prompt_settings` で無視される。
- フォルダ内の **`*.yaml` は名前順に深いマージ**（同じキーは後勝ち）。
- 編集後はプロセス再起動で反映（`prompt_settings` はキャッシュ読み込み）。
- プレースホルダーは `{name}`。差し込みは `config/prompt_settings.py` の `format_prompt` / `get_prompt_str` を参照。
