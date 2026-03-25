# 実行時の `output/` の見方（工程テスト用）

`OUTPUT_DIR`（既定: リポジトリ直下の `output/`）は **`.gitignore` 対象**です。ここにだけ生成物が溜まります。

**工程テスト**（preflight〜gemini_step のフォルダ説明・コマンド・検証知見）は **[`PIPELINE_TESTING.md`](../PIPELINE_TESTING.md)**（リポジトリ直下）。本書はサイト出力や従来レイアウトに重点。

## 工程テストを 1 フォルダにまとめる

プリフライト・フェーズ1・作業分岐のスナップショットを **同一の親ディレクトリ** に置く方法です。

1. **一括（推奨）**  
   `python3 scripts/pipeline_test_snapshots.py`  
   → `output/pipeline_test_runs/<UTC>/` を作成し、その下に `preflight_snapshots/`・`phase1_snapshots/`・`work_branch_snapshots/` が並びます（別スクリプトで同じ親に `phase2_snapshots/`・`gemini_step_tests/` を追加することも可）。`00_pipeline_test_manifest.json` に各ステップの保存パスが入ります。

2. **環境変数**  
   `PIPELINE_TEST_RUN_DIR=output/pipeline_test_runs/my_run` を `.env` に書いたうえで、従来どおり各スクリプトを個別実行すると、上記と同じレイアウトの **その親** 配下に出力されます。

3. **個別スクリプト**  
   `scripts/preflight_before_process_case.py` / `phase1_from_preflight_cases.py` / `work_branch_from_preflight_cases.py` に `--run-dir <親パス>` を付けても同じです。

従来の `output/preflight_snapshots/` 直下のみの配置も、変数・`--run-dir` を付けなければそのままです。

## 1 案件あたりのパス

### フェーズ2中: LLM 1 回ごとのトレース（`sites` より先にできる）

```
output/<レコード番号>/llm_steps/<NNN>_gemini_generate_content/
output/<レコード番号>/llm_steps/<NNN>_manus_…/   （Manus 呼び出し時）
```

`main.py` が `begin_case_llm_trace` したあと、**Gemini の `generate_content` が終わるたび**に `001_` `002_` … と増える（`input.md` / `output.md`）。**`output/sites/` はまだ無い時間帯でも、ここには書き込まれる。**

### フェーズ3以降: サイト本体

```
output/sites/<パートナー名>-<レコード番号>/
```

`<…>` は `main.py` が `site_generator.generate_site` に渡す `site_name` と同じです。

## Manus 待ちでも消えない Gemini 正本（チェックポイント）

`output/sites/<site_name>/` はフェーズ3で `generate_site` が**既存を退避削除**するため、**フェーズ2が Manus のポーリングで止まっているあいだ**はそこに `llm_raw_output/` がまだありません。

その対策として、**Gemini マニュアル全手順が終わって Manus リファクタに入る直前**に、次へ **同一形式の生出力**が書かれます（`generate_site` の対象外なので残ります）。

```
output/phase2_llm_checkpoints/<site_name>/pre_manus/
  README.txt
  00_checkpoint.json
  canvas_before_manus.md
  llm_raw_output/gemini_steps/<pipe>/…   （サイト正本と同じ .md / *_prompt.txt / _model.txt）
```

`<site_name>` は main の `output/sites/<site_name>/` と同じ `{パートナー名}-{レコード番号}`（`/` `\` `:` のみ `_` に置換、日本語社名はそのまま）。Manus 完了後は従来どおりサイト配下の `llm_raw_output/` にフル正本が保存されます。

## フェーズ2直後の正本（`phase2_complete`）

TEXT_LLM が **正常終了した直後**（`generate_site` より前）に、次へ **サイト正本と同形式の `llm_raw_output/`** が必ず書かれます。フェーズ3で `output/sites/` がまだ無い・消えた・途中で落ちた場合でも、ここを見ればフェーズ2の成果が追えます。

```
output/phase2_complete/<site_name>/README.txt
output/phase2_complete/<site_name>/llm_raw_output/…
```

`output/` 全体は **`.gitignore`** のため、Git には載りません（ローカル・CI 成果物として扱う）。

## フォルダの意味（時間順・ざっくり）

| 中身 | いつできるか | 何を見るか |
|------|----------------|------------|
| `TECH_REQUIREMENTS.md` | サイトディレクトリ作成直後 | 共通技術要項（参照用） |
| `llm_raw_output/` | TEXT_LLM 直後、`write_llm_raw_artifacts` 後 | **フェーズ2の正本**（spec の長文キーが `.md`、`site_build_prompt.txt`、Gemini は `gemini_steps/<pipe>/step_*.md`（応答）と `step_*_prompt.txt`（API に渡した入力）、Manus は `manus_refactor_task_prompt.txt`） |
| `app/`, `components/`, `public/`, `package.json` など | `apply_contract_outputs_to_site_dir` 成功後 | **フェンス適用後のサイト本体** |
| `.next/`, `node_modules/` | ローカルで `npm install` / `npm run build` 後 | ビルドキャッシュ（push に含まないことが多い） |

## 工程テストのコツ

1. **まず** `llm_raw_output/*.md` で、その案件の LLM 生出力を確認する。  
2. **次に** `app/page.tsx` 等が増えているかでフェンス適用の成否を見る。  
3. ビルドログはターミナルまたは `SITE_IMPLEMENTATION_ENABLED` 周りのログを参照。

プラン別に `llm_raw_output` に出るキー名は `modules/llm/llm_raw_output.py` の `_SPEC_LLM_KEYS` を参照。

## プリフライト（`process_case` 直前まで）

本番 `WebsiteBot.run()` と同じ順序で、起動検証 → 列見出し → `get_pending_cases` のあと **`BOT_MAX_CASES` で先頭 N 件に切り詰める** ところまでを **1 回だけ** 走らせ、JSON をまとめて保存します（`process_case` は呼びません）。

**本番で「1 件だけ」実行する検証**（`BOT_MAX_CASES=1 python main.py` と同じキュー）に揃える場合は、プリフライトも同じ変数を付けます。

```bash
BOT_MAX_CASES=1 python3 scripts/preflight_before_process_case.py
```

全件キューだけ確認する場合（`04` が多くなる）は `BOT_MAX_CASES` を付けないか、`.env` で未設定にします。

```bash
python3 scripts/preflight_before_process_case.py
```

保存先は `output/preflight_snapshots/<UTC時刻>/`（`01`〜`04` の JSON と `README.txt`）。`03` に `fetched_count`（API から取った件数）と `after_bot_max_cases`（切り詰め後）が入ります。設定 NG や `SPREADSHEET_HEADERS_STRICT` 下での列不一致は本番同様に終了コード 1 になります。

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
