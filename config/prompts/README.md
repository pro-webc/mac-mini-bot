# プロンプト YAML（工程フォルダ）

要望・仕様の生成は **`llm_mock`** が主で、これら YAML は **将来の実 LLM 接続時**や **画像パイプライン**で参照されます。現状よく効くのは **画像**（`image_generation/`）と **共通技術要件**（`common/`）です。

```
config/prompts/
├── common/
├── requirement_extraction/
├── spec_generation/
├── site_implementation/
└── image_generation/    # PIL プレースホルダ用テンプレ（placeholder 等）
```

- **フォルダ名** = マージ後の第1キー（例: `image_generation.cursor_agent_system`）。
- フォルダ内の **`*.yaml` は名前順に深いマージ**（同じキーは後勝ち）。
- 編集後はプロセス再起動で反映（`prompt_settings` はキャッシュ読み込み）。
- プレースホルダーは `{name}`。差し込みは `config/prompt_settings.py` の `format_prompt` / `get_prompt_str` を参照。
