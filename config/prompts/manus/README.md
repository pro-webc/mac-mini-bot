# Manus 用プロンプト（手作業マニュアルと本番 API の対応）

## 手作業でやっていること（要約）

**タイミング**: Gemini（Canvas 相当）で単一ファイルのソースが出た直後。

**Manus に任せる一連作業**（GitHub 連携前提で、ここまで完了するとリモートに push 済みになる想定）:

1. **Git リポジトリ作成** — `propagate-webcreation` ワークスペース、private、`propagate-webcreation/DefaultSetting` テンプレ。**リポジトリ名**は `test-run-レコード番号`（レコード番号はスプレッドシートの値を GitHub 向けに正規化。ボットは `build_basic_lp_refactor_user_prompt` で展開）。**ディスクリプション**は**パートナー名**列と同一の1行のみ。工程テスト・本番共通。同名リポジトリが既にあれば**即終了**。
2. **リファクタリング** — クローンし、リファクタ指示書どおりに単一 Canvas ソースを App Router 構成へ分割。
3. **画像** — `ImagePlaceholder` 等を洗い出し、nanobananaPro で生成し `/public/images/` に実装、`next/image` へ置換。
4. **検証と push** — `npm run build`、失敗時は自己修復ループ、成功後に push。

**手作業時の入力（チャット上のイメージ）**:

1. オーケストレーション用プロンプト（先頭）— 手順1の **先方名**（スプレッドシートのパートナー名列）を案件どおりに差し替え。
2. **リファクタリング指示書**（長文のためファイル添付になりやすい）。
3. **Gemini Canvas 生成ソース**（同上）。

画面上は「プロンプト + 2 ファイル」に見える。モデルは **Manus 1.6 のみ**（他モデル禁止）。

**運用メモ**（コード外）:

- 生成コストが高いため **1 回試して失敗したら担当者へ報告**、同じ案件で何度も繰り返さない。
- クレジットが **5000 を切ったら**プラン確認のうえ担当者へ。
- ログインアカウント等は組織の手作業マニュアルに従う。

---

## リポジトリ内のファイルと本番の組み立て

| ファイル | 内容 |
|----------|------|
| `orchestration_prompt.txt` | 上記 1〜4 のオーケストレーション（Repo・リファクタ・画像・build/push）。`{{MANUS_REPO_NAME}}` / `{{MANUS_REPO_DESCRIPTION}}` を `build_basic_lp_refactor_user_prompt` が展開。末尾に Manus 1.6 指定あり。 |
| `refactoring_instruction_handwork.txt` | 手作業で「リファクタリング指示書」として貼る本文と同一系統。 |
| `bot_deploy_instruction.txt` | （API 時のみ）`BOT_DEPLOY_GITHUB_URL:` 行の出し方。`{{MANUS_DEPLOY_GITHUB_REPO_HINT_LINE}}` は環境変数 `MANUS_DEPLOY_GITHUB_REPO_HINT` があるとき `bot_deploy_repo_hint_line.txt` から生成。 |
| `bot_deploy_repo_hint_line.txt` | 上記プレースホルダ用の1行（`{{MANUS_DEPLOY_GITHUB_REPO_HINT}}` を2箇所）。 |

**結合**（手作業の「3 ブロック」を 1 本文にしたもの）:

`modules.basic_lp_refactor_gemini.build_basic_lp_refactor_user_prompt` は次を**この順**で連結する（手作業と同じ本文＋プレースホルダ展開のみ。GitHub 垢の注意などは `orchestration_prompt.txt` に書く）。

1. `orchestration_prompt.txt`（`{{MANUS_REPO_NAME}}`・`{{MANUS_REPO_DESCRIPTION}}` を `record_number`・`partner_name`（パートナー名列）から展開済み）
2. 区切り `---`
3. `refactoring_instruction_handwork.txt` 全文
4. `===== BEGIN_CANVAS_SOURCE =====` … Gemini 出力 … `===== END_CANVAS_SOURCE =====`
5. （既定）`MANUS_PROVIDES_DEPLOY_GITHUB_URL=true` のとき、`bot_deploy_instruction.txt`（＋任意で `bot_deploy_repo_hint_line.txt`）を末尾に追加（手作業マニュアルには無い API 用。`false` で無効化可）

**API 送信**: `modules/manus_refactor.py` が `POST {MANUS_API_BASE}/v1/tasks` に上記を `prompt` として渡す。`MANUS_TASK_CONNECTORS`（未設定時は公式の GitHub コネクタ UUID 1 件）を `connectors` に付与。OAuth は [Connectors](https://open.manus.im/docs/connectors) のとおり manus.im で事前連携。`MANUS_AGENT_PROFILE`・`MANUS_TASK_MODE` は `config.config`。

---

## 工程テストで切り出すときの観点

- **入力（Canvas 相当の本文）**: **Gemini 工程テストの最終ステップの応答ファイル**をそのまま使う。
  - **STANDARD-CP**: `scripts/gemini_standard_cp_step15_from_phase1.py`（**15/15・手順7-4**）が保存する **`gemini_step_tests/<UTC>/02_response_step_7_4.txt`**
  - **BASIC LP** など他プラン: マニュアルチェーンの **最終手順の `02_response_*.txt`**（LP は多くの場合 **手順8-3** の `02_response_step_8_3.txt`）
- **案件メタ**: 同じ run の `phase1_snapshots/<UTC>/01_case_meta.json` の **パートナー名・レコード番号**（Manus の「先方名」はパートナー名と同一）。
- **期待**: 手作業と同じプロンプト構造になること（中身の diff は `orchestration` / `refactoring` の改訂で管理）。
- **検証**: Manus 返答のフェンス群・任意の `BOT_DEPLOY_GITHUB_URL` 行（有効時）。

詳細はリポジトリ直下の **`PIPELINE_TESTING.md`**（工程テスト）および **`docs/LLM_PIPELINE.md`**（Manus 節）を参照。
