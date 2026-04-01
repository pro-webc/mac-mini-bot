# 再開スクリプトガイド & 障害対応表

パイプライン障害が発生したとき、**ログの該当行を引用してフェーズを特定**し、適切な再開手段を選ぶためのガイド。

> **前提**: `.cursor/rules/log-reading-discipline.mdc` のルールに従い、**ログを読まずに原因を推測しない**。

---

## 再開スクリプトの選択フロー

```
障害発生
  │
  ├─ どのフェーズで止まった？
  │
  ├─ Phase 2（TEXT_LLM）途中 ─────────────────────────────────────┐
  │   ├─ STANDARD-CP の step 7-3 でタイムアウト                   │
  │   │   └─ _resume_from_step73.py                              │
  │   ├─ STANDARD-CP のそれ以外のステップで中断                    │
  │   │   └─ _resume_standard_cp.py（最終ステップを自動検出）      │
  │   └─ BASIC LP / BASIC CP / ADVANCE の Claude 中断             │
  │       └─ 再開手段なし → BOT_ONLY_RECORD_NUMBER で再実行       │
  │                                                               │
  ├─ Phase 2 完了・Manus 完了後 ──────────────────────────────────┤
  │   └─ post-Manus 検証 → Phase 3〜5                            │
  │       └─ _resume_from_post_manus.py                           │
  │                                                               │
  ├─ Phase 3〜5 途中 ────────────────────────────────────────────┤
  │   └─ site_dir の状態で自動判定                                │
  │       └─ _resume_from_phase3_or_deploy.py                     │
  │                                                               │
  └─ Manus のみ再実行（Claude は完了済み）────────────────────────┤
      └─ scripts/_resume_from_post_manus.py で再実行               │
```

---

## 再開スクリプト一覧

| スクリプト | 再開ポイント | 前提条件 | コマンド |
|-----------|-------------|---------|---------|
| `_resume_from_step73.py` | STANDARD-CP step 7-3 以降 | `llm_steps/001〜015` が保存済み | `python scripts/_resume_from_step73.py <record>` |
| `_resume_standard_cp.py` | STANDARD-CP 任意ステップ以降 | `llm_steps/` に途中までの出力あり | `python scripts/_resume_standard_cp.py <record>` |
| `_resume_from_post_manus.py` | post-Manus 検証 → Phase 3〜5 | `llm_steps/*_manus_refactor/output.md` あり | `python scripts/_resume_from_post_manus.py <record> [record2 ...]` |
| `_resume_from_phase3_or_deploy.py` | Phase 3 or 5（自動判定） | `site_dir` が存在 | `RESUME_RECORD=<record> python scripts/_resume_from_phase3_or_deploy.py` |

**関連する環境変数:**

| 変数 | 用途 |
|------|------|
| `BOT_ONLY_RECORD_NUMBER` | 特定案件のみ処理（再開時は必須） |
| `FORCE_LOCAL_PUSH=true` | `_resume_from_phase3_or_deploy.py` で Manus URL を無視しローカル push |
| `STANDARD_CP_REFACTOR_AFTER_MANUAL` | 再開時に Manus リファクタを含めるか |

---

## 障害対応表

### Phase 1: ヒアリング抽出・作業分岐

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `ヒアリング本文が空のため案件をスキップ` | スプレッドシートの AH 列が空 or URL のみ | シートのヒアリング列を確認。`SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL` 設定も確認 |
| `必須項目が未入力のため案件に着手しません` | `SPREADSHEET_REQUIRED_CASE_FIELDS` のいずれかが空 | シートの該当列を確認 |

### Phase 2: TEXT_LLM（Claude CLI 多段）

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `claude CLI が見つかりません` | `claude` コマンドが PATH にない | `npm install -g @anthropic-ai/claude-code` |
| `Claude CLI がタイムアウトしました（Ns）` | `CLAUDE_CLI_TIMEOUT_SEC` 超過 | `.env` でタイムアウト延長。`llm_steps/` で最後に成功したステップを確認し、再開スクリプトを選択 |
| `Claude CLI の出力が空です。stderr:` | CLI が応答を返さなかった | stderr のメッセージを確認。認証・ネットワーク・サブスクリプション状態を確認 |
| `Claude CLI の JSON パースに失敗` | CLI 出力が JSON でない | CLI バージョン確認。`--output-format json` 対応か確認 |
| `プレースホルダが未置換です` | プロンプトテンプレートの `{{KEY}}` に対応する値がない | `config/prompts/` の該当 `.txt` とパイプラインの `_subst` 呼び出しを確認 |
| `結合要望テキストが短すぎます` | Claude の応答が極端に短い | `llm_steps/` で各ステップの `output.md` を確認。プロンプト改善が必要 |
| `ヒアリングシート本文が空です` | `hearing_block` に空文字が渡された | Phase 1 の抽出結果を確認 |

### Phase 2: Manus リファクタ

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `MANUS_API_KEY が未設定です` | `.env` の `MANUS_API_KEY` が空 | API キーを設定 |
| `Manus タスク作成に失敗` / HTTP ≠ 200 | API エラー | レスポンス本文を確認。API の認証・レート制限 |
| `Manus ポーリング … status=failed` | Manus 側でタスク失敗 | エラー内容を確認。プロンプト・ソースコードの問題の可能性 |
| `pending 状態が 600 秒を超えました` | Manus が入力待ちで停止 | `MANUS_INTERACTIVE_MODE=false` を確認 |
| `Manus リファクタがタイムアウト` | `MANUS_REFACTOR_TIMEOUT_SEC` 超過 | タイムアウト延長。Manus タスク URL を手動確認 |
| `GetTask 404` | タスク ID の伝播遅延 or 無効 | 通常はリトライで解決。繰り返すなら Manus 側を確認 |

### Phase 3: サイト準備

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `shallow clone に失敗しました` | Manus の GitHub URL が無効 or 権限不足 | URL の存在を `git ls-remote` で確認。`GITHUB_TOKEN` の repo 権限を確認 |
| `サイトファイルを1件も適用できませんでした` | フェンス付きマークダウンの解析失敗 | `llm_steps/` の Manus 出力を確認。フェンス形式が正しいか |

### Phase 4: ビルド

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `package.json がありません` | サイトディレクトリの構成不備 | Phase 3 の出力を確認。テンプレートの問題の可能性 |
| `npm install 失敗` | 依存解決エラー | `package.json` の依存関係と Node.js バージョンを確認 |
| `npm run build 失敗` | Next.js ビルドエラー | ログ末尾の Next.js / TypeScript エラーを確認。`_resume_from_phase3_or_deploy.py` で再ビルド |
| `npm install/ci がタイムアウトしました` | ネットワーク or 依存が重い | ネットワーク確認、`node_modules` を削除して再実行 |
| `page.tsx の本数が契約ページ数と一致しません` | ルート構成の不一致 | Manus のリファクタ結果を確認。`SITE_BUILD_ENFORCE_CONTRACT_PAGE_TSX_COUNT` を一時的に `false` にして確認 |

### Phase 5: デプロイ

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `GITHUB_TOKENが必要です` | トークン未設定 | `.env` を確認 |
| `リポジトリ '…' は既に存在します` | 同名リポが GitHub 上に存在 | 既存リポを確認・削除するか、別名で実行 |
| `GitHubプッシュエラー` | push 失敗 | 認証・リポ権限・ブランチ保護を確認 |
| `VERCEL_TOKENが必要です` | Vercel トークン未設定 | `.env` を確認 |
| `Vercelデプロイエラー` | Vercel API 失敗 | レスポンス本文を確認。プロジェクト名・チーム ID・GitHub 連携状態 |
| `デプロイURLが閲覧できません` | デプロイ保護 or URL 不正（**警告のみ・処理は続行**） | `VERCEL_FORCE_PUBLIC_DEPLOYMENTS=true` を確認 |

### 起動時

| ログの目印 | 原因 | 対応 |
|-----------|------|------|
| `[設定]` + エラー | `validate_startup_config` 失敗 | `BOT_CONFIG_CHECK=1 python main.py` で設定を確認 |
| `スプレッドシート列検出で例外` | シートのヘッダー行が想定と違う | `fix_spreadsheet_headers_av_aw.py` or シートの列構成を確認 |

---

## ログの読み方（クイックリファレンス）

**grep で探すキーワード:**

```bash
# フェーズの区切り
grep '【フェーズ' <logfile>

# エラー全般
grep -E '案件処理エラー|Bot実行エラー|予期しないエラー' <logfile>

# Claude CLI
grep -E 'Claude CLI|タイムアウト' <logfile>

# Manus
grep -E 'Manus タスク|Manus ポーリング|status=' <logfile>

# ビルド
grep -E 'npm install|npm run build|package.json' <logfile>

# デプロイ
grep -E 'GitHub|Vercel|デプロイ' <logfile>
```

**llm_steps でのステップ確認:**

```bash
# 最後に成功したステップを確認
ls -la output/<record>/llm_steps/

# 各ステップの入出力を確認
cat output/<record>/llm_steps/<NNN>_*/output.md | head -50
```

---

## 工程テスト用スクリプト（本番案件でない検証向け）

| スクリプト | 用途 |
|-----------|------|
| `pipeline_test_manus_only.py` | Claude 出力ファイルを入力に Manus のみ実行 |
| `pipeline_test_deploy_only.py` | GitHub URL を入力に Vercel デプロイのみ実行 |
| `pipeline_test_snapshots.py` | プリフライト → Phase 1 → 作業分岐のスナップショット一括取得 |

詳細は [PIPELINE_TESTING.md](../pipeline/PIPELINE_TESTING.md) を参照。
