# 工程テスト・段階 Gemini テスト（まとめ）

`main.py` の `process_case` を回さずに、**プリフライト → フェーズ1 → 作業分岐 →（任意で）フェーズ2単体・STANDARD-CP の Gemini 段階**までを切り出して検証する手順です。  
生成物はすべて **`output/` 以下**（`.gitignore`）です。

---

## 1 ランの親ディレクトリ

`scripts/pipeline_test_snapshots.py` で作成するレイアウトを基準にします。

```text
output/pipeline_test_runs/<run_UTC>/
├── 00_pipeline_test_manifest.json   # 一括スクリプト実行時
├── README.txt
├── preflight_snapshots/<UTC>/
├── phase1_snapshots/<UTC>/
├── work_branch_snapshots/<UTC>/
├── phase2_snapshots/<UTC>/          # 任意
└── gemini_step_tests/<UTC>/         # 任意（STANDARD-CP 段階テスト）
```

- **`<run_UTC>`** … その検証セッションの親。`.env` の **`PIPELINE_TEST_RUN_DIR`**、または各スクリプトの **`--run-dir`** で揃える。
- 直下の **`<UTC>`** … 各スクリプト実行ごとのタイムスタンプ（複数世代が並ぶことがある）。

キューを本番と同じ長さにしたいときは、一括の前に `BOT_MAX_CASES=1` などを付けます（プリフライトと同じ考え方）。

---

## フォルダ別：何が入るか・何を見るか

| フォルダ | 主なスクリプト | 中身の要点 | 確認するとよいこと |
|----------|----------------|------------|---------------------|
| **`preflight_snapshots/`** | `preflight_before_process_case.py` / 一括の前半 | `01_startup_validation.json`・`04_pending_cases.json`（キュー）など | 起動検証・列見出し・`BOT_MAX_CASES` 適用後の待ち案件 |
| **`phase1_snapshots/`** | `phase1_from_preflight_cases.py` / 一括 | `hearing_sheet_content.txt`・`appo_memo.txt`・`sales_notes.txt`・`01_case_meta.json`・`02_hearing_bundle_summary.json` | フェーズ1と同じ `extract_hearing_bundle` の結果・本文空なら本番でもスキップ |
| **`work_branch_snapshots/`** | `work_branch_from_preflight_cases.py` / 一括 | `01_work_branches.json`（行ごとの `branch_final` 等） | `main` と同じ作業分岐（BASIC→LP 寄せ含む） |
| **`phase2_snapshots/`** | `phase2_from_phase1_snapshot.py` | `requirements_result.yaml`・`spec.yaml`・`02_summary.yaml`・`00_source.json` 等 | TEXT_LLM 単体の入出力（本番フェーズ2相当） |
| **`gemini_step_tests/`** | `gemini_standard_cp_step1`〜`step10` `_from_phase1.py` | 1〜10回目それぞれ `01_prompt_*`・`02_response_*`・`meta.json`（10回目は `step_5`・タブ⑤継続） | STANDARD-CP の **API 1/15〜10/15** を段階的に手作業マニュアルと突き合わせる用途 |

### `preflight_snapshots/<UTC>/`（ファイル一覧の目安）

| ファイル | 意味 |
|----------|------|
| `01_startup_validation.json` | 起動時バリデーション結果 |
| `02_header_issues.json` | 列見出しまわり（該当時） |
| `03_pending_cases_summary.json` | 取得件数・切り詰め後件数など |
| `04_pending_cases.json` | **以降の工程テストの入力**となる案件リスト |
| `README.txt` | 説明 |

### `phase1_snapshots/<UTC>/`

| ファイル | 意味 |
|----------|------|
| `00_source.json` | 入力 `04` のパス・`case_index` |
| `01_case_meta.json` | `row_number`・`record_number`・`partner_name`・`contract_plan` |
| `hearing_sheet_content.txt` | LLM 原料（ヒアリング本文） |
| `appo_memo.txt` / `sales_notes.txt` | 同バンドルのメモ |
| `02_hearing_bundle_summary.json` | 文字数・`would_skip_in_main` |
| `README.txt` | 説明 |

### `work_branch_snapshots/<UTC>/`

| ファイル | 意味 |
|----------|------|
| `00_source.json` | 入力 `cases_json`・任意で `phase1_snapshot_dir` |
| `01_work_branches.json` | 案件ごとの分岐メタ（`branch_final` 等） |
| `README.txt` | 説明 |

### `phase2_snapshots/<UTC>/`

| ファイル | 意味 |
|----------|------|
| `00_source.json` | `phase1_dir`・work_branch JSON の有無・解決方法 |
| `01_case_meta.json` | フェーズ1からのコピー |
| `requirements_result.yaml` / `spec.yaml` | TEXT_LLM の出力（UTF-8 テキスト） |
| `02_summary.yaml` | キー一覧・文字数などの要約 |
| `README.txt` | 説明 |

### `gemini_step_tests/<UTC>/`（STANDARD-CP・タブ①〜④ / タブ⑤ / タブ⑥）

実行のたびに **新しい `<UTC>` フォルダ**が増えます。**1回目〜各回**を別フォルダに保存します。

| ファイル | 意味 |
|----------|------|
| `00_source.json` | `phase1_dir`・`run_root`・直前ステップの `prev_gemini_dir` 等 |
| `01_prompt_step_1_1.txt` / `02_response_step_1_1.txt` | API 1/15 |
| `01_prompt_step_1_2_and_1_3.txt` / `02_response_step_1_2_and_1_3.txt` | API 2/15（**手順1-2 と 1-3 を連結した1送信**。手作業マニュアルと同じ） |
| `01_prompt_step_2.txt` / `02_response_step_2.txt` | API 3/15（手順2・6ページ構成など・`gemini_standard_cp_step3_from_phase1.py`） |
| `01_prompt_step_3_1.txt` / `02_response_step_3_1.txt` | API 4/15（手順3-1・TOPのみ・`gemini_standard_cp_step4_from_phase1.py`） |
| `01_prompt_step_3_2.txt` / `02_response_step_3_2.txt` | API 5/15（手順3-2・サービスページ・`gemini_standard_cp_step5_from_phase1.py`・**4回目の3-1で `history` 復元**・同一チャット継続） |
| `01_prompt_step_3_3.txt` / `02_response_step_3_3.txt` | API 6/15（手順3-3・会社概要・**3-1+3-2 で2往復 `history` 復元**） |
| `01_prompt_step_3_4.txt` / `02_response_step_3_4.txt` | API 7/15（手順3-4・お問い合わせ・**3往復履歴復元**・`gemini_standard_cp_step7_from_phase1.py` は本番の手順7-1ではない） |
| `01_prompt_step_3_5.txt` / `02_response_step_3_5.txt` | API 8/15（手順3-5・残りページ・**4往復 `history` 復元**・タブ④終了） |
| `01_prompt_step_4.txt` / `02_response_step_4.txt` | API 9/15（手順4・配色・**新規チャット**・`gemini_standard_cp_step9_from_phase1.py`） |
| `01_prompt_step_5.txt` / `02_response_step_5.txt` | API 10/15（手順5・**9回目の手順4で `history` 復元**・2・3回目の応答で置換・`gemini_standard_cp_step10_from_phase1.py`） |
| `01_prompt_step_7_1.txt` 〜 `02_response_step_7_4.txt` 等 | API **11〜15/15**（タブ⑥・手順7-1〜7-4・`gemini_standard_cp_step11`〜**`step15`**）。**工程テストの最終応答**は **`02_response_step_7_4.txt`**（15/15） |
| `meta.json` | 文字数・`step`・`gemini_call_index_1based`（1〜15） |
| `README.txt` | 説明 |

本番の **BASIC-CP / STANDARD-CP / ADVANCE-CP / BASIC LP** でも、タブ②はいずれも **手順1-2と1-3を連結した1送信**です（API 総数はプランごとに異なる）。詳細は **`docs/LLM_PIPELINE.md`**。

---

## コマンド早見

| やりたいこと | コマンド（リポジトリルート） |
|--------------|-----------------------------|
| プリフライト＋フェーズ1＋作業分岐を一括 | `python3 scripts/pipeline_test_snapshots.py` |
| 上記の親を指定 | `python3 scripts/pipeline_test_snapshots.py --run-dir output/pipeline_test_runs/my_run` |
| TEXT_LLM だけ（フェーズ1入力） | `python3 scripts/phase2_from_phase1_snapshot.py --phase1-dir .../phase1_snapshots/<UTC>` |
| STANDARD-CP Gemini **1/15**（手順1-1） | `python3 scripts/gemini_standard_cp_step1_from_phase1.py --phase1-dir .../phase1_snapshots/<UTC>` |
| STANDARD-CP Gemini **2/15**（手順1-2＋1-3 **連結**） | `python3 scripts/gemini_standard_cp_step2_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<1回目UTC>/` |
| STANDARD-CP Gemini **3/15**（手順2・タブ③） | `python3 scripts/gemini_standard_cp_step3_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<2回目UTC>/` |
| STANDARD-CP Gemini **4/15**（手順3-1・タブ④1通目） | `python3 scripts/gemini_standard_cp_step4_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<3回目UTC>/`（`00_source.json` から2回目フォルダを辿り手順1-3を解決。解決できないときは `--step1-3-response`） |
| STANDARD-CP Gemini **5/15**（手順3-2・タブ④2通目） | `python3 scripts/gemini_standard_cp_step5_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<4回目UTC>/`（`01_prompt_step_3_1.txt` と `02_response_step_3_1.txt` でチャット履歴を復元） |
| STANDARD-CP Gemini **6/15**（手順3-3・タブ④3通目） | `python3 scripts/gemini_standard_cp_step6_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<5回目UTC>/`（5回目の `00_source.json` から4回目を辿り3-1を解決。辿れないときは `--step3-1-prompt` / `--step3-1-response`） |
| STANDARD-CP Gemini **7/15**（手順3-4・タブ④4通目） | `python3 scripts/gemini_standard_cp_step7_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<6回目UTC>/`（6→5→4 の `prev_gemini_dir` で3-1〜3-2を解決。スクリプト名の step7 は **段階テスト7回目** で本番の手順7-1とは別） |
| STANDARD-CP Gemini **8/15**（手順3-5・タブ④5通目＝タブ④終了） | `python3 scripts/gemini_standard_cp_step8_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<7回目UTC>/`（7→6→5→4 のチェーンで3-1〜3-3を解決。欠けるときは `--step3-3-*` 等） |
| STANDARD-CP Gemini **9/15**（手順4・タブ⑤1通目） | `python3 scripts/gemini_standard_cp_step9_from_phase1.py --phase1-dir .../phase1_snapshots/<UTC>/`（タブ④の成果物は不要。ヒアリング本文のみ） |
| STANDARD-CP Gemini **10/15**（手順5・タブ⑤2通目） | `python3 scripts/gemini_standard_cp_step10_from_phase1.py --phase1-dir 同上 --prev-gemini-dir .../gemini_step_tests/<9回目UTC>/ --step1-3-dir .../<2回目UTC>/ --step2-dir .../<3回目UTC>/`（9回目で手順4を履歴復元。2・3回目は応答ファイルのディレクトリ） |
| STANDARD-CP Gemini **11〜15/15**（タブ⑥・手順7-1〜7-4） | `gemini_standard_cp_step11_from_phase1.py` 〜 **`step15_from_phase1.py`**（**最終 15/15** は手順7-4。成果物 **`02_response_step_7_4.txt`**） |

**Manus 工程テストに渡す Gemini 最終出力（STANDARD-CP）**: 段階テストを最後まで進めた **15 回目**のフォルダ `gemini_step_tests/<UTC>/` 内の **`02_response_step_7_4.txt`** が、いわゆる「工程テストの最後の応答」（Canvas 単一ファイル相当の本文）。案件メタは同じ run の `phase1_snapshots/.../01_case_meta.json` と揃える。詳細は **`config/prompts/manus/README.md`**（工程テストの観点）。

`.env` の **`PIPELINE_TEST_RUN_DIR`** を親に合わせると、各スクリプトの既定出力先がその配下になります（`config.config.pipeline_run_root_for_resolve`）。**同じ親に後から足す**ときは、上表のスクリプトを同じ順で実行すればよい（`phase1` が `.../phase1_snapshots/...` にある場合、一部スクリプトは `--run-dir` を省略できる）。

---

## 本番パイプラインとの対応（ざっくり）

| 本番（`process_case`） | 工程テストのフォルダ |
|------------------------|----------------------|
| キュー取得〜待ち案件 | `preflight_snapshots`（`04`） |
| フェーズ1 ヒアリング抽出 | `phase1_snapshots` |
| 作業分岐解決 | `work_branch_snapshots` |
| フェーズ2 TEXT_LLM | `phase2_snapshots`（単体）／本番は続けて `output/sites/...` |
| STANDARD-CP の Gemini 多段（合計 API **15 回**・段階テストは step1〜**step15**） | `gemini_step_tests`（**最終応答**は多くの場合 **`02_response_step_7_4.txt`**） |

本番の LLM 回数・モジュール対応は **`docs/LLM_PIPELINE.md`** の表を正とします。

---

## 手作業マニュアルとの突き合わせ

- STANDARD-CP の **タブ①** は `gemini_standard_cp_step1_from_phase1.py`、**タブ②** は `gemini_standard_cp_step2_from_phase1.py`（1回目の `02_response_step_1_1.txt` が必要）、**タブ③・手順2** は `gemini_standard_cp_step3_from_phase1.py`（2回目の `02_response_step_1_2_and_1_3.txt` が必要）、**タブ④の手順3-1** は `gemini_standard_cp_step4_from_phase1.py`（3回目の `02_response_step_2.txt` と、2回目経由の手順1-3本文）、**手順3-2** は `gemini_standard_cp_step5_from_phase1.py`（4回目の3-1で `start_chat(history)` を1往復復元）、**手順3-3** は `gemini_standard_cp_step6_from_phase1.py`（5回目の3-2と、4回目の3-1で2往復復元）、**手順3-4** は `gemini_standard_cp_step7_from_phase1.py`（6回目の3-3と、5・4回目経由で3往復復元。スクリプト名の step7 は **段階テスト7回目** で、本番タブ⑥の **手順7-1** とは別）、**手順3-5（タブ④最終）** は `gemini_standard_cp_step8_from_phase1.py`（7回目の3-4と、6→5→4 経由で4往復復元）、**タブ⑤・手順4** は `gemini_standard_cp_step9_from_phase1.py`（フェーズ1のヒアリング本文のみ・新規チャット）、**手順5** は `gemini_standard_cp_step10_from_phase1.py`（9回目の手順4で履歴復元＋2・3回目の応答で `step_5.txt` 置換）。
- **タブ⑤の手順6**および**タブ⑥**は本モジュール内で連続実行されるため、段階ファイルが必要なら同様のスクリプト追加が必要です。

---

## 成果物レビュー：静かな欠損（特に手順3-2）

段階テストの突き合わせで次が分かっている。

- **`02_response_step_3_2.txt`（API 5/15）** は、6ページ構成のうち **サービス系が複数ページに分かれる案件**では **1回の応答で複数ページ分の原稿**を載せる。`max_output_tokens` に達すると **後半ページのセクションが丸ごと無い**まま終わることがある（末尾が文の途中で切れていないか、`02_response_step_2.txt` のセクション見出しと数を照合するとよい）。
- **手順7（タブ⑥・コード生成）で途中切れに気づいてトークン上限を上げた場合**でも、**既に欠けた手順3-2の内容は履歴から自動復元されない**。揃えたいときは **API 5/15 から同じ `prev_gemini_dir` チェーンで再実行**するか、本番相当なら **該当案件を手順3-2以降からやり直す**。
- 本番のマニュアル多段 Gemini は **`GEMINI_MANUAL_MAX_OUTPUT_TOKENS` を全 API で共通利用**する（手順7だけ大きい、という分岐はない）。既定・上限は **`config/config.py`**、運用上の整理は **`docs/ARTICLE_LLM_MULTI_STAGE_MAX_OUTPUT_TOKENS.md`**、不具合・運用の表は下記「テスト・検証で見つかった…」を参照。

---

## テスト・検証で見つかった不具合・齟齬・運用知見

段階テストや手作業マニュアルとの突き合わせで判明したものです（コード修正済みのものと、設定・再実行が必要な運用知見を含む）。

| 種別 | 内容 |
|------|------|
| **コードバグ** | `modules/standard_cp_gemini_manual.py` の `run_standard_cp_gemini_manual_pipeline` で、手順1-2 のテンプレート置換に **未定義の変数 `hear`** を参照していた（`NameError`）。**`hearing_sheet_content`** を渡すよう修正済み。段階テストの「1回目だけ」では未到達で、本番のフルチェーンで初めて顕在化しうる箇所だった。 |
| **マニュアル不一致（タブ②）** | 手作業マニュアルは **手順1-2 と 1-3 を連結して1送信**だが、実装は **`send_message` を2回**に分けていた。その結果、2回目の送信までモデルが「読み込みだけ」の短文で止まり、**手順1-3相当の長い整理稿が出にくい**（段階テストでは応答が極端に短いなど）。**BASIC-CP / STANDARD-CP / ADVANCE-CP / BASIC LP** すべてで **1メッセージに連結**へ統一し、各プランの **Gemini API 回数の定数**も減算して整合。 |
| **段階テスト成果物のファイル名** | タブ②を連結にしたあとは、2回目の保存ファイルを **`01_prompt_step_1_2_and_1_3.txt`** / **`02_response_step_1_2_and_1_3.txt`** とした（旧・`step_1_2` のみのファイル名は旧挙動）。 |
| **データ表記（バグではない）** | 代表者名などが手作業貼り付けとスナップショットで **「羽」と「羽」のように別コードポイント**になることがある。**`fetch_hearing_sheet` は Unicode 正規化しておらず**、ソースはスプレッドシート／フォーム側の字形のまま。必要ならシート上の表記を揃えるか、取り込み後の正規化方針を別途決める。 |
| **`max_output_tokens` 打ち切り（手順3-2 ほか）** | 手順3-2（API 5/15）は **複数サービスページの原稿を1応答**にまとめる。上限不足だと **2ページ目側の末尾セクションが生成されない**ことがある（構成案手順2にはあるが `02_response_step_3_2.txt` に無い、など）。**手順7で TSX が途中切れしたときに初めて気づきやすい**が、同じ打ち切りがより上流で起きている可能性がある。対策: `.env` の **`GEMINI_MANUAL_MAX_OUTPUT_TOKENS`**（本番は **全 Gemini 呼び出しで共通**・既定 65536・上限 131072）、`finish_reason` / 応答末尾の完結性の確認。 |
| **履歴に残った欠損は手順7の修正だけでは戻らない** | トークン上限を手順7付近で引き上げても、**すでに切れた手順3-2の assistant メッセージはチャット履歴に残る**。欠損セクションをコードに出したい場合は、**手順3-2（API 5/15）以降を同じチェーンでやり直す**（またはフェーズ1からフル再実行）必要がある。 |

### 補足（設計メモ）

多段パイプライン全体の `max_output_tokens` 落とし穴と対策の整理は **`docs/ARTICLE_LLM_MULTI_STAGE_MAX_OUTPUT_TOKENS.md`** を参照。

---

## 関連ドキュメント

| パス | 内容 |
|------|------|
| **`docs/OUTPUT_LAYOUT.md`** | `output/` 全般・`output/sites/...` |
| **`docs/DIRECTORY_GUIDE.md`** | リポジトリ全体の地図 |
| **`docs/LLM_PIPELINE.md`** | LLM / Manus の割当・タブ②連結の注記 |
| **`docs/ARTICLE_LLM_MULTI_STAGE_MAX_OUTPUT_TOKENS.md`** | 多段 API の `max_output_tokens` 不足による「静かな途中切れ」 |

単体テスト（pytest）と CI 用 ruff は **`README.md`** の「品質・Lint」を参照してください。
