# LLM プロンプト（工程フォルダ）

```
config/prompts/
├── text_llm/
├── common/
├── requirement_extraction/
├── spec_generation/
├── site_implementation/
└── image_generation/    # 用途別に複数 YAML（placeholder / cursor_agent / gemini_openai）
```

- **フォルダ名** = マージ後の第1キー（例: `image_generation.cursor_agent_system`）。
- フォルダ内の **`*.yaml` は名前順に深いマージ**（同じキーは後勝ち）。
- 編集後はプロセス再起動で反映（`prompt_settings` はキャッシュ読み込み）。
- プレースホルダーは `{name}`。差し込みは `config/prompt_settings.py` の `format_prompt` / `get_prompt_str` を参照。
