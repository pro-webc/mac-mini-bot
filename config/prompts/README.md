# プロンプト（YAML）

**実行時に読み込むのは `config/prompts/common/*.yaml` だけです。**  
（`get_technical_spec_prompt_block()` → サイト土台生成時の技術要件テキスト）

契約プラン別の Gemini マニュアルは **`*.txt`（`basic_lp_manual/` 等）** から別モジュールが読みます。ここに置いても **自動ではマージされません**。

- フォルダ内の **`*.yaml` は名前順に深いマージ**（同じキーは後勝ち）。
- 編集後はプロセス再起動で反映（`prompt_settings` はキャッシュ読み込み）。
- プレースホルダーは `{name}`。差し込みは `config/prompt_settings.py` の `format_prompt` / `get_prompt_str` を参照。
