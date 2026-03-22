"""TEXT_LLM 一式（要望抽出・仕様生成・パース・生出力保存）。

- 入口: ``text_llm_stage.run_text_llm_stage``（プランは ``if/elif`` → 各 ``*_gemini_manual``）
- BASIC 系の台本組み立て: ``basic_cp_spec`` / ``basic_lp_spec``（マニュアルから参照）
- 共通: ``llm_pipeline_common`` / ``site_script_parse`` / ``spec_json_extract``
- 正本保存: ``llm_raw_output`` / パス検証: ``llm_output_files``
"""
