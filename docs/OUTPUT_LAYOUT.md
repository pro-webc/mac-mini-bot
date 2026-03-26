# 多段 LLM の入出力トレースと `output/` の見方

`OUTPUT_DIR`（既定: リポジトリ直下の `output/`）は **`.gitignore` 対象**です。ここに LLM の全入出力と生成物が蓄積されます。

**`output/` はこのシステムの自己改善サイクルの根幹**です。全案件の全 LLM 呼び出しが記録されており、プロンプト改善の根拠データとして機能します。

**工程テスト**（preflight〜`claude_step_tests` 等のフォルダ説明・コマンド・検証知見）は **[`PIPELINE_TESTING.md`](../PIPELINE_TESTING.md)**（リポジトリ直下）。

---

## ステップトレースで多段 LLM を辿る（実践ガイド）

### 全体像: ステップ番号とパイプラインの対応

案件を実行すると `output/<レコード番号>/llm_steps/` に **1 回の LLM 呼び出し = 1 サブフォルダ** が連番で増えていきます。以下は BASIC LP（11 回チェーン）の例です。

```
output/11346/llm_steps/
├── 001_claude_cli_generate/   ← 手順1-1: ヒアリング整形（単発）
│   ├── input.md               ← 送ったプロンプト全文
│   └── output.md              ← LLM の応答全文
├── 002_claude_cli_chat/       ← 手順1-2+1-3: 事業理解の凝縮（チャット開始）
│   ├── input.md
│   └── output.md
├── 003_claude_cli_chat/       ← 手順2: ページ構成・セクション設計
├── 004_claude_cli_chat/       ← 手順3: テキストライティング
├── ...
├── 010_claude_cli_chat/       ← 手順7-*: コード生成（Canvas tsx）
├── 011_claude_cli_chat/       ← 最終: Canvas 完成
└── 013_manus_refactor/        ← Manus リファクタ（設定有効時のみ）
    ├── input.md
    └── output.md（または error.txt）
```

### ステップ番号とプラン別チェーンの対応

ステップ番号はプラン・案件ごとに異なりますが、種別名（`kind`）で段階がわかります。

| `kind`（ディレクトリ名の `NNN_` 以降） | どこで記録されるか | 意味 |
|----------------------------------------|-------------------|------|
| `claude_cli_generate` | `claude_manual_common.generate_text` | Claude Code CLI 単発呼び出し（チャットセッションなし。手順 1-1 等） |
| `claude_cli_chat` | `ClaudeCLIChat.send_message` | Claude Code CLI チャット（セッション継続。手順 1-2 以降の多段ステップ） |
| `manus_refactor` | `manus_refactor.manus_basic_lp_refactor_with_poll` | Manus API によるリファクタ（タスク作成 → ポーリング → 完了） |

各プランの呼び出し回数は以下のとおりです（Manus リファクタは設定有効時のみ末尾に +1）。

| プラン | モジュール | CLI 呼び出し回数 | 典型的なステップ範囲 |
|--------|-----------|-----------------|---------------------|
| BASIC LP | `basic_lp_claude_manual.py` | 11 回 | `001` 〜 `011` + Manus |
| BASIC | `basic_cp_claude_manual.py` | 10 回 | `001` 〜 `010` + Manus |
| STANDARD | `standard_cp_claude_manual.py` | 15 回 | `001` 〜 `015` + Manus |
| ADVANCE | `advance_cp_claude_manual.py` | 16 回 | `001` 〜 `016` + Manus |

### `input.md` と `output.md` の中身

| ファイル | 内容 | 書式 |
|----------|------|------|
| `input.md` | LLM に送ったプロンプト全文 | Markdown テキスト。`claude_cli_generate` は `claude -p` に渡した 1 プロンプト。`claude_cli_chat` はユーザーメッセージ（初回は会話履歴を含む場合あり）。`manus_refactor` はタスク作成時の全文（オーケストレーション + リファクタ指示 + Canvas ソース） |
| `output.md` | LLM の応答全文 | Markdown テキスト。Claude CLI の場合は `result` JSON の `text`。Manus の場合は完了タスクの `output_text` |
| `error.txt` | エラー発生時の例外メッセージ | `output.md` の代わりに保存。例: `RuntimeError: Manus タスクがタイムアウトしました（2700.0s）` |

### 品質問題の特定手順（典型ワークフロー）

1. **問題のある案件の `llm_steps/` を開く**

```bash
ls output/11346/llm_steps/
# 001_claude_cli_generate/  002_claude_cli_chat/  ...  013_manus_refactor/
```

2. **各ステップの出力を確認して問題箇所を特定する**

```bash
# ページ構成（手順2）の出力を見る
cat output/11346/llm_steps/003_claude_cli_chat/output.md

# コード生成（Canvas）の出力を見る
cat output/11346/llm_steps/010_claude_cli_chat/output.md
```

3. **問題のステップの `input.md` からプロンプトを確認する**

```bash
cat output/11346/llm_steps/003_claude_cli_chat/input.md
```

4. **対応するプロンプトファイルを特定して改善する**

    - `input.md` のプロンプト冒頭にある手順番号（例: `【手順.2】`）でステップファイルを特定
    - → `config/prompts/*_manual/step_2.txt` を編集
    - 全プラン共通の品質問題 → `config/prompts/common/technical_spec_prompt_block.txt` にルール追加

5. **改善効果を検証する**

```bash
python3 scripts/phase2_from_phase1_snapshot.py   # 同じ入力でフェーズ2を再実行
```

### 案件横断でステップを比較する

同じステップ番号の出力を複数案件で比較すると、プロンプトの効果が見えます。

```bash
# 全案件のステップ 003（ページ構成）の出力を一覧
for d in output/*/llm_steps/003_*/; do echo "=== $d ==="; head -20 "$d/output.md"; echo; done
```

---

## 記録の 3 層構造

このシステムは LLM の入出力を **3 つの粒度** で保存し、品質改善の異なる観点を支えています。

### 第 1 層: リアルタイムステップトレース（`llm_step_trace`）

**目的**: 全 LLM 呼び出しの入出力を 1 回ごとに自動保存し、「どのステップで何が起きたか」を追跡可能にする。

```
output/<レコード番号>/llm_steps/
├── 001_claude_cli_generate/       ← TEXT_LLM 呼び出し #1（Claude Code CLI）
│   ├── input.md                    ← 送ったプロンプト全文
│   └── output.md                   ← LLM の応答全文
├── 002_claude_cli_chat/           ← TEXT_LLM 呼び出し #2（マルチターン時は chat）
│   ├── input.md
│   └── output.md
├── ...
├── 011_manus_refactor/            ← Manus への入力と応答
│   ├── input.md
│   └── output.md（または error.txt）
└── 016_manus_refactor/            ← 最終リファクタ
```

`modules.claude_manual_common` が Claude Code CLI（`claude -p`）を `subprocess` で実行し、各ターンで `record_llm_turn` を呼ぶため、**TEXT_LLM の入出力が自動記録**されます（単発は `claude_cli_generate`、マルチターンは `claude_cli_chat`）。Manus は `record_llm_turn` で明示呼び出しです。**失敗時は `error.txt`** に例外メッセージが保存されます。

### 第 2 層: チェックポイント（`llm_raw_output`）

**目的**: LLM の生出力を**加工前の原文のまま**保存し、後工程の不具合（パーサ・ビルド）と LLM の出力品質の問題を切り分ける。

```
output/phase2_llm_checkpoints/<site_name>/pre_manus/   ← TEXT_LLM（Claude CLI）完了〜Manus 開始前
output/phase2_complete/<site_name>/llm_raw_output/      ← フェーズ2完了直後
output/sites/<site_name>/llm_raw_output/                ← フェーズ3完了後の正本
```

`llm_raw_output.py` の冒頭 docstring に設計意図が明記されています: **「パーサやビルドが失敗しても、ここに残したテキストが AI の答えの記録になる」**。Manus が長時間ブロックしても TEXT_LLM 分は `pre_manus/` に退避済みです。

### 第 3 層: 構造化メタデータ

**目的**: 案件・プラン・モデル・文字数などを機械可読な形で残し、傾向分析を可能にする。

- `spec.yaml` / `requirements_result.yaml` — LLM 出力の構造化正本
- `00_checkpoint.json` — タイムスタンプ・プラン・モデル名・文字数
- `02_summary.json` — Manus リファクタの結果メタ

### 自己改善サイクルでの活用

| 改善の観点 | 参照する記録 | 具体例 |
|------------|-------------|--------|
| 特定ステップの品質 | 第 1 層の `NNN_*/output.md` | 「ステップ 2（ページ構成）でセクションが薄い」→ `step_2.txt` を改善 |
| TEXT_LLM vs Manus の切り分け | 第 1 層の最終 TEXT_LLM（Claude CLI）と Manus の両方 | 「Canvas tsx は良いが Manus の分割で壊れる」→ `refactoring_instruction_handwork.txt` を改善 |
| 全体傾向の把握 | 第 3 層の `spec.yaml` / `summary.json` | 「STANDARD プランで文字数が少ない案件が多い」→ コンテンツ生成ステップを強化 |
| パーサ vs LLM の切り分け | 第 2 層の raw output vs `app/` | 「raw に正しいコードがあるのに `app/` に反映されない」→ パーサ側のバグ |

---

## トレースの仕組み（コードリファレンス）

### アーキテクチャ

```
main.py                              modules/claude_manual_common.py     modules/manus_refactor.py
  │                                       │                                   │
  │ begin_case_llm_trace(record)          │ generate_text()                   │ manus_..._with_poll()
  │  → contextvars にルートをセット         │  → record_llm_turn(               │  → record_llm_turn(
  │  → ステップ番号を 0 にリセット          │      kind="claude_cli_generate")   │      kind="manus_refactor")
  │                                       │                                   │
  │                                       │ ClaudeCLIChat.send_message()      │
  │                                       │  → record_llm_turn(               │
  │                                       │      kind="claude_cli_chat")      │
  │                                       │                                   │
  │ end_case_llm_trace()                  │                                   │
  │  → contextvars を無効化               │                                   │
```

### 主要 API（`modules/llm/llm_step_trace.py`）

| 関数 | 引数 | 役割 |
|------|------|------|
| `begin_case_llm_trace(record_number)` | レコード番号（文字列） | `OUTPUT_DIR/<record>/llm_steps/` を作成し、`contextvars` にトレースルートをセット。ステップ番号を 0 にリセット |
| `end_case_llm_trace()` | なし | トレースを無効化（`contextvars` を `None` に）。次の `begin` まで `record_llm_turn` は no-op になる |
| `record_llm_turn(*, kind, input_text, output_text, error_text)` | `kind`: ディレクトリ名の種別（`claude_cli_generate` 等）。`input_text`: プロンプト。`output_text` または `error_text`: 応答またはエラー | ステップ番号を +1 して `{seq:03d}_{kind}/` を作り、`input.md` と `output.md`（または `error.txt`）を保存 |
| `ensure_case_trace_dir(record_number)` | レコード番号（文字列） | `OUTPUT_DIR/<record>/` と `llm_steps/` の作成のみ（トレースの開始はしない） |

### 呼び出しフロー

1. `main.py` の `process_case` が案件開始時に `begin_case_llm_trace(record_number)` を呼ぶ
2. Claude CLI の各呼び出し（`generate_text` / `ClaudeCLIChat.send_message`）が `record_llm_turn` を自動で呼ぶ
3. Manus リファクタ（`manus_refactor.py`）は成功・失敗のいずれでも `record_llm_turn` を明示呼び出し
4. `process_case` の `finally` で `end_case_llm_trace()` が呼ばれ、トレースが終了

**`contextvars` による案件スコープ**: トレースルートは `contextvars.ContextVar` で管理されるため、`begin` 〜 `end` の間のどこから `record_llm_turn` を呼んでも正しい案件ディレクトリに書き込まれます。`begin` 前や `end` 後の呼び出しは自動で無視されます（no-op）。

### 新しい LLM 呼び出しにトレースを追加する場合

既存の Claude CLI（`generate_text` / `ClaudeCLIChat`）経由であれば自動記録されるため、追加作業は不要です。新しい LLM プロバイダを追加する場合は、呼び出し箇所で直接 `record_llm_turn` を呼びます。

```python
from modules.llm.llm_step_trace import record_llm_turn

try:
    response = call_new_llm(prompt)
    record_llm_turn(kind="new_provider_name", input_text=prompt, output_text=response)
except Exception as e:
    record_llm_turn(kind="new_provider_name", input_text=prompt, error_text=f"{type(e).__name__}: {e}")
    raise
```

---

## 1 案件あたりのパス（時系列）

### フェーズ2中: LLM 1 回ごとのトレース（`sites` より先にできる）

```
output/<レコード番号>/llm_steps/<NNN>_claude_cli_generate/
output/<レコード番号>/llm_steps/<NNN>_claude_cli_chat/
output/<レコード番号>/llm_steps/<NNN>_manus_…/   （Manus 呼び出し時）
```

`main.py` が `begin_case_llm_trace` したあと、**Claude Code CLI の呼び出し（TEXT_LLM）が終わるたび**に `001_` `002_` … と増えます（`input.md` / `output.md`）。**`output/sites/` はまだ無い時間帯でも、ここには書き込まれます。**

### フェーズ3以降: サイト本体

```
output/sites/<パートナー名>-<レコード番号>/
```

`<…>` は `main.py` が `site_generator.generate_site` に渡す `site_name` と同じです。

## Manus 待ちでも消えない TEXT_LLM 正本（チェックポイント）

`output/sites/<site_name>/` はフェーズ3で `generate_site` が**既存を退避削除**するため、**フェーズ2が Manus のポーリングで止まっているあいだ**はそこに `llm_raw_output/` がまだありません。

その対策として、**TEXT_LLM（Claude CLI）マニュアル全手順が終わって Manus リファクタに入る直前**に、次へ **同一形式の生出力**が書かれます（`generate_site` の対象外なので残ります）。

```
output/phase2_llm_checkpoints/<site_name>/pre_manus/
  README.txt
  00_checkpoint.json
  canvas_before_manus.md
  llm_raw_output/claude_steps/<pipe>/…   （サイト正本と同じ .md / *_prompt.txt / _model.txt）
```

`<site_name>` は main の `output/sites/<site_name>/` と同じ `{パートナー名}-{レコード番号}`（`/` `\` `:` のみ `_` に置換、日本語社名はそのまま）。Manus 完了後は従来どおりサイト配下の `llm_raw_output/` にフル正本が保存されます。

## フェーズ2直後の正本（`phase2_complete`）

TEXT_LLM が **正常終了した直後**（`generate_site` より前）に、次へ **サイト正本と同形式の `llm_raw_output/`** が必ず書かれます。フェーズ3で `output/sites/` がまだ無い・消えた・途中で落ちた場合でも、ここを見ればフェーズ2の成果が追えます。

```
output/phase2_complete/<site_name>/README.txt
output/phase2_complete/<site_name>/llm_raw_output/…
```

`output/` 全体は **`.gitignore`** のため、Git には載りません（ローカル・CI 成果物として扱う）。

## フォルダの意味（時間順）

| 中身 | いつできるか | 何を見るか |
|------|----------------|------------|
| `TECH_REQUIREMENTS.md` | サイトディレクトリ作成直後 | 共通技術要項（参照用） |
| `llm_raw_output/` | TEXT_LLM 直後、`write_llm_raw_artifacts` 後 | **フェーズ2の正本**（spec の長文キーが `.md`、`site_build_prompt.txt`、TEXT_LLM は `claude_steps/<pipe>/step_*.md`（応答）と `step_*_prompt.txt`（Claude Code CLI に渡した入力）。Manus は `manus_refactor_task_prompt.txt`） |
| `app/`, `components/`, `public/`, `package.json` など | `apply_contract_outputs_to_site_dir` 成功後 | **フェンス適用後のサイト本体** |
| `.next/`, `node_modules/` | ローカルで `npm install` / `npm run build` 後 | ビルドキャッシュ（push に含まないことが多い） |

---

## 工程テストを 1 フォルダにまとめる

プリフライト・フェーズ1・作業分岐のスナップショットを **同一の親ディレクトリ** に置く方法です。

1. **一括（推奨）**  
   `python3 scripts/pipeline_test_snapshots.py`  
   → `output/pipeline_test_runs/<UTC>/` を作成し、その下に `preflight_snapshots/`・`phase1_snapshots/`・`work_branch_snapshots/` が並びます（別スクリプトで同じ親に `phase2_snapshots/`・`claude_step_tests/` を追加することも可）。`00_pipeline_test_manifest.json` に各ステップの保存パスが入ります。

2. **環境変数**  
   `PIPELINE_TEST_RUN_DIR=output/pipeline_test_runs/my_run` を `.env` に書いたうえで、従来どおり各スクリプトを個別実行すると、上記と同じレイアウトの **その親** 配下に出力されます。

3. **個別スクリプト**  
   `scripts/preflight_before_process_case.py` / `phase1_from_preflight_cases.py` / `work_branch_from_preflight_cases.py` に `--run-dir <親パス>` を付けても同じです。

従来の `output/preflight_snapshots/` 直下のみの配置も、変数・`--run-dir` を付けなければそのままです。

## 工程テストのコツ

1. **まず** `llm_raw_output/*.md` で、その案件の LLM 生出力を確認する。  
2. **次に** `app/page.tsx` 等が増えているかでフェンス適用の成否を見る。  
3. ビルドログはターミナルまたは `SITE_IMPLEMENTATION_ENABLED` 周りのログを参照。

プラン別に `llm_raw_output` に出るキー名は `modules/llm/llm_raw_output.py` の `_SPEC_LLM_KEYS` を参照。

## プリフライト（`process_case` 直前まで）

本番 `WebsiteBot.run()` と同じ順序で、起動検証 → 列見出し → `get_pending_cases` のあと **`BOT_MAX_CASES` で先頭 N 件に切り詰める** ところまでを **1 回だけ** 走らせ、JSON をまとめて保存します（`process_case` は呼びません）。

```bash
BOT_MAX_CASES=1 python3 scripts/preflight_before_process_case.py   # 1 件だけ
python3 scripts/preflight_before_process_case.py                    # 全件キュー
```

保存先は `output/preflight_snapshots/<UTC時刻>/`（`01`〜`04` の JSON と `README.txt`）。`02` に自動検出した列位置マッピング、`03` に `fetched_count`（API から取った件数）と `after_bot_max_cases`（切り詰め後）が入ります。設定 NG や列検出失敗は本番同様に終了コード 1 になります。

## フェーズ1スナップショット（ヒアリング抽出）

`04_pending_cases.json` を入力に `extract_hearing_bundle` だけ実行し、`output/phase1_snapshots/<UTC>/` に `.txt` と要約 JSON を保存します。

```bash
python3 scripts/phase1_from_preflight_cases.py [04_pending_cases.json]
```

## 契約プラン作業分岐スナップショット

`04` の各行について `main.process_case` と同じ作業分岐（`resolve_work_branch_with_basic_lp_override`、BASIC 時はサイトタイプシート参照）を算出し、`output/work_branch_snapshots/<UTC>/01_work_branches.json` に保存します。

```bash
python3 scripts/work_branch_from_preflight_cases.py [04_pending_cases.json]
```
