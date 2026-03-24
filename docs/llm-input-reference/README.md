# サイト生成時に LLM へ渡る情報（索引）

本フォルダは、`config/prompts/` のテキストと `docs/LLM_PIPELINE.md` に沿った**実装フロー**から、モデル（Gemini / Manus）に渡る入力とルールをジャンル別に整理したものです。

## 派生版 `mac-mini-bot-v2` と LLM 2 段

- **開発主軸ブランチ**: `mac-mini-bot-v2`（上流 `main` との関係はルート `README.md` を参照）。
- **LLM 2 段**: **第 1 段 Gemini**（`*_manual/*.txt`）で要件・Canvas 相当を生成し、**第 2 段 Manus**（`manus/*.txt`）でリファクタ・実装・push を担う構成を**正**として本索引を保守する。

| ファイル | 内容 |
|----------|------|
| [runtime-inputs.md](./runtime-inputs.md) | コードから差し込まれるデータ（ヒアリング本文・案件メタ・プレースホルダ・チェーン出力の受け渡し） |
| [site-structure-rules.md](./site-structure-rules.md) | LP/CP のセクション順・必須セクション・ワイヤ・原稿ルールなど**構成** |
| [design-rules.md](./design-rules.md) | 配色・雰囲気・デザイン指示書・UI 品質・ヒーロー・FAQ 等の**見た目・トーン** |
| [technical-requirements.md](./technical-requirements.md) | スタック、コンポーネント分割、CSS 順序、アイコン・画像・地図、共通ブロックと `TECH_REQUIREMENTS.md` |
| [git-and-deploy-rules.md](./git-and-deploy-rules.md) | Manus 向け GitHub リポジトリ命名、`BOT_DEPLOY_GITHUB_URL`、ボット側 push/Vercel との関係 |
| [content-and-expression.md](./content-and-expression.md) | コピー・絵文字禁止・フォーム・A11y など**文言と表現** |

## 処理フロー（要約）

1. **Gemini（第1フェーズ）**  
   `modules.llm.text_llm_stage.run_text_llm_stage` → 契約プランに応じて `*_gemini_manual` が `config/prompts/*_manual/*.txt` を読み、`ExtractedHearingBundle` 由来の値で `{{...}}` を置換しながら多段で `generate_content` / `send_message`。
2. **仕様 dict**  
   マニュアル完了後、`build_*_spec_dict` 等でパースし、`technical_spec.common_requirements` に `config.config.COMMON_TECHNICAL_SPEC` がマージされる（`modules.llm.llm_pipeline_common.apply_common_technical_to_spec`）。
3. **出力先**  
   `SiteGenerator` が `get_common_technical_spec_prompt_block()` の内容を `TECH_REQUIREMENTS.md` としてサイトディレクトリに書く（LLM への再送ではなく参照用・push 対象）。
4. **Manus（第2フェーズ・任意）**  
   `BASIC_LP_REFACTOR_AFTER_MANUAL` 等が有効なとき、Gemini の Canvas 相当の単一ソースを `build_basic_lp_refactor_user_prompt` で `config/prompts/manus/*.txt` と連結して Manus API に送信。

詳細はリポジトリの `docs/LLM_PIPELINE.md` を参照してください。
