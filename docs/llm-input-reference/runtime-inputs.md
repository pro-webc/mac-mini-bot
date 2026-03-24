# ランタイム入力（コードから LLM へ渡るデータ）

## 入口: TEXT_LLM ステージ

`modules.llm.text_llm_stage.run_text_llm_stage` が `ExtractedHearingBundle` と案件メタを各 Gemini マニュアルパイプラインに渡します。

| 引数（キーワード） | 意味 |
|-------------------|------|
| `hearing_sheet_content` | ヒアリングシート抽出本文（手順 1-1 の `{{HEARING_BLOCK}}` 源） |
| `appo_memo` | アポメモ |
| `sales_notes` | 営業メモ（空でなければ「営業メモ・その他先方情報」として `{{APPO_MEMO}}` に連結） |
| `contract_plan` | 契約プラン文字列 |
| `partner_name` | スプレッドシートのパートナー名（結合ログ・仕様・Manus のリポジトリ説明等で使用） |
| `record_number` | レコード番号（Manus の `bot-{番号}-{先方名}` 用） |
| `existing_site_url` | 既存サイト URL（空ならヒアリングから推定し `{{EXISTING_SITE_URL_BLOCK}}` に） |

## プレースホルダ（`{{NAME}}`）の代表例

各 `modules.*_gemini_manual` の `_subst` が `config/prompts/*_manual/*.txt` 内の `{{...}}` を置換します。

| プレースホルダ | 主な意味 |
|----------------|----------|
| `HEARING_BLOCK` | ヒアリング全文 |
| `STEP_1_1_OUTPUT` | 手順 1-1 のモデル応答 |
| `STEP_1_3_OUTPUT` / `HEARING_1_3_OUTPUT` | タブ②相当の顧客情報まとめ等 |
| `APPO_MEMO` | アポ＋営業メモブロック |
| `EXISTING_SITE_URL_BLOCK` | 既存サイト URL または「記載なし」指示 |
| `STEP_2_OUTPUT` … | 前段の応答を次プロンプトに連鎖 |
| `HP_COLOR_CLIENT` / `MOOD_CLIENT` | BASIC 系では自動実行時に「ヒアリングを参照せよ」旨の指示文に差し替え |
| `REFERENCE_URL_BLOCK` | `modules.hearing_url_utils.reference_site_url_from_hearing` の結果またはフォールバック文 |
| `BLOG_PAGE_LINE` | STANDARD/ADVANCE の step_2 でブログ有無等を制御する行（パイプライン側で生成） |

## チェーン出力の再利用（概念）

- **新規チャット**はマニュアル上の「タブ」境界に対応（プランごとに回数・手順が異なる）。
- 同一チャット内では `send_message` で手順を積み上げ、直前の応答を次のプロンプト本文に埋め込まずともコンテキストとして保持される場合と、明示的に `{{STEP_*}}` で埋め込む場合がある。

## Manus 向け（第2フェーズ）

`modules.basic_lp_refactor_gemini.build_basic_lp_refactor_user_prompt` が次を連結します。

1. `orchestration_prompt.txt`（`{{MANUS_REPO_NAME}}` / `{{MANUS_REPO_DESCRIPTION}}` を `record_number`・`partner_name` で展開）
2. `---`
3. `refactoring_instruction_handwork.txt`
4. `===== BEGIN_CANVAS_SOURCE =====` + **Gemini 最終段の Canvas 単一ファイル相当** + `END_CANVAS_SOURCE`
5. （既定）`MANUS_PROVIDES_DEPLOY_GITHUB_URL` が真なら `bot_deploy_instruction.txt`（＋任意で `bot_deploy_repo_hint_line.txt`）

GitHub トークン等の秘密はプロンプトに含めません（Manus の GitHub コネクタ側で認証）。
