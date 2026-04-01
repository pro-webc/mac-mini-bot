# 可観測性設計（Phase D）

## 目的

パイプラインの状態を**常時把握**し、異常を**早期検知**する。ダッシュボードによる全体俯瞰と、アラートによる即時対応を両立させる。

---

## 可観測性の 3 本柱

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   メトリクス   │  │    ログ      │  │   アラート    │
│              │  │              │  │              │
│ 成功率       │  │ 構造化ログ    │  │ Slack 通知   │
│ 平均スコア   │  │ フェーズ別    │  │ 閾値ベース   │
│ 処理時間     │  │ JSON 形式    │  │ 連続失敗検知 │
│ コスト       │  │ 検索可能     │  │ スコア急落   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
               ┌─────────────────┐
               │  ダッシュボード   │
               │  （Web UI）      │
               └─────────────────┘
```

---

## 1. メトリクス

### 収集対象

| カテゴリ | メトリクス | 単位 | 収集タイミング |
|---------|----------|------|-------------|
| **パイプライン** | 処理件数（成功/失敗/スキップ） | 件 | バッチ完了時 |
| | フェーズ別所要時間 | 秒 | 各フェーズ完了時 |
| | フェーズ別成功率 | % | 各フェーズ完了時 |
| **品質** | 軸別平均スコア | 0-100 | Phase 6 完了時 |
| | スコア分布（四分位） | 0-100 | 日次集計 |
| | 閾値未満率 | % | 日次集計 |
| **コスト** | ステップ別トークン消費 | tokens | 各 LLM 呼び出し時 |
| | 案件あたり推定コスト | USD | 案件完了時 |
| | Manus API 呼び出し回数 | 回 | Manus 完了時 |
| **外部サービス** | Claude CLI レスポンス時間 | 秒 | 各呼び出し時 |
| | Manus タスク完了時間 | 秒 | ポーリング完了時 |
| | Vercel デプロイ時間 | 秒 | デプロイ完了時 |

### 保存形式

```
output/metrics/
├── pipeline_runs.jsonl          ← 1 行 = 1 案件の実行記録
├── daily_summary.jsonl          ← 日次集計
└── cost_tracking.jsonl          ← コスト追跡
```

**`pipeline_runs.jsonl` の 1 行:**

```json
{
  "timestamp": "2026-03-31T14:30:00+09:00",
  "record_number": "12345",
  "partner_name": "サンプル株式会社",
  "contract_plan": "STANDARD",
  "status": "success",
  "phases": {
    "phase1": { "duration_sec": 3, "status": "success" },
    "phase2": { "duration_sec": 420, "status": "success", "llm_calls": 15, "total_tokens": 185000 },
    "phase3": { "duration_sec": 12, "status": "success" },
    "phase4": { "duration_sec": 45, "status": "success" },
    "phase5": { "duration_sec": 90, "status": "success" },
    "phase6": { "duration_sec": 30, "status": "success" }
  },
  "scores": { "technical": 95, "structural": 80, "design": 72, "content": 68, "overall": 76 },
  "cost_estimate_usd": 2.40,
  "deploy_url": "https://example.vercel.app"
}
```

---

## 2. 構造化ログ

### 現在のログ → 構造化ログへの移行

**現在**: `logging.info()` でテキストログ → `bot.log`

**目標**: JSON 構造化ログ（既存のテキストログと並行出力）

| フィールド | 型 | 説明 |
|-----------|---|------|
| `timestamp` | ISO 8601 | イベント発生時刻 |
| `level` | string | INFO / WARNING / ERROR |
| `phase` | string | phase1〜phase6 |
| `step` | string | step_1_1 等（Phase 2 のみ） |
| `record_number` | string | 案件番号 |
| `event` | string | イベント種別（下表） |
| `details` | object | イベント固有データ |
| `duration_sec` | float | 経過時間（該当する場合） |

**イベント種別:**

| event | 発生タイミング | details に含むもの |
|-------|-------------|------------------|
| `pipeline_start` | `process_case()` 開始 | record_number, partner_name, plan |
| `phase_start` | 各フェーズ開始 | phase 番号 |
| `phase_complete` | 各フェーズ完了 | phase 番号, duration_sec, status |
| `llm_call_start` | Claude CLI 呼び出し開始 | step, prompt_length |
| `llm_call_complete` | Claude CLI 呼び出し完了 | step, output_length, tokens, duration_sec |
| `manus_task_start` | Manus API 呼び出し | task_id |
| `manus_task_complete` | Manus タスク完了 | task_id, duration_sec, deploy_url |
| `build_result` | npm run build 完了 | success, error_count |
| `deploy_complete` | Vercel デプロイ完了 | deploy_url, duration_sec |
| `evaluation_complete` | 評価完了 | scores |
| `pipeline_error` | エラー発生 | phase, step, error_type, message |
| `pipeline_complete` | `process_case()` 完了 | total_duration_sec, status |

---

## 3. アラート

### アラート条件

| 条件 | 重要度 | 通知先 | アクション |
|------|--------|--------|----------|
| 連続 3 件失敗 | **Critical** | Slack + メール | パイプライン一時停止を検討 |
| overall スコア 50 未満 | **High** | Slack | 該当案件の手動レビュー |
| overall スコア移動平均が前週比 -10 | **High** | Slack | プロンプト劣化の調査 |
| Phase 2 タイムアウト（>1800秒） | **Medium** | Slack | Claude CLI の状態確認 |
| Manus タスク pending > 30分 | **Medium** | Slack | Manus API の状態確認 |
| 日次処理件数 0 件（営業日） | **Low** | Slack | キュー条件・Sheets の確認 |
| 推定コストが日次予算超過 | **Medium** | Slack | バッチ上限の調整検討 |

### 通知フォーマット（Slack）

```
🔴 [Critical] mac-mini-bot: 連続失敗
━━━━━━━━━━━━━━━━━━━━━━━━━
直近 3 件が連続で失敗しました

失敗案件:
  #12345 サンプル株式会社 → Phase 2 step_8_3 タイムアウト
  #12346 テスト商事 → Phase 4 ビルドエラー
  #12347 デモ工業 → Phase 2 step_5 空レスポンス

最終成功: 2026-03-31 10:00
━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. ダッシュボード

### 画面構成

```
┌─────────────────────────────────────────────────────────┐
│  mac-mini-bot ダッシュボード                [最終更新: 14:30]│
├─────────────┬─────────────┬─────────────┬──────────────┤
│  今日の処理   │  成功率      │  平均スコア   │  推定コスト    │
│    12 件     │   83%       │    74        │   $28.80     │
├─────────────┴─────────────┴─────────────┴──────────────┤
│                                                         │
│  スコア推移グラフ（直近 30 日）                             │
│  ─── overall  ─── technical  ─── design  ─── content   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  プラン別スコア分布（箱ひげ図）                              │
│  BASIC LP | BASIC | STANDARD | ADVANCE                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  直近の処理結果一覧                                       │
│  # | パートナー | プラン | スコア | ステータス | URL         │
│  ──┼──────────┼──────┼──────┼────────┼────────         │
│  ... │         │       │       │         │               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 技術選定

| 選択肢 | メリット | デメリット |
|--------|---------|----------|
| **Streamlit**（推奨） | Python で完結。`output/metrics/` を直接読める。セットアップ最小 | インタラクティブ性に限界 |
| Grafana + SQLite | 高機能。アラート統合あり | インフラ追加が必要 |
| Google Sheets ダッシュボード | 既存 Sheets と統合可能 | リアルタイム性に限界 |

---

## モジュール構成

```
modules/
└── observability/
    ├── __init__.py
    ├── structured_logger.py     ← 構造化ログ出力（既存ロガーをラップ）
    ├── metrics_collector.py     ← メトリクス収集・JSONL 書き込み
    ├── alerter.py               ← アラート条件判定・Slack 送信
    └── dashboard/
        ├── app.py               ← Streamlit ダッシュボード
        └── charts.py            ← グラフ描画ヘルパー
```

---

## 実装の優先順

| 順番 | 対象 | 理由 |
|------|------|------|
| 1 | `metrics_collector.py` | JSONL に書くだけ。既存コードへの変更が最小 |
| 2 | `structured_logger.py` | 既存 `logging` をラップ。段階的に移行可能 |
| 3 | `alerter.py` | Slack Webhook 1 つで即実装。運用効果が高い |
| 4 | `dashboard/` | メトリクスが溜まってから。Streamlit で素早くプロトタイプ |

---

## 関連ドキュメント

| 文書 | 役割 |
|------|------|
| [EVOLUTION_ROADMAP.md](./EVOLUTION_ROADMAP.md) | 全体ロードマップ |
| [AUTO_SCORING.md](./AUTO_SCORING.md) | 評価基盤（品質メトリクスの源泉） |
| [OUTPUT_LAYOUT.md](../pipeline/OUTPUT_LAYOUT.md) | 既存の出力構造 |
| [RESUME_AND_TROUBLESHOOTING.md](../system-rules/RESUME_AND_TROUBLESHOOTING.md) | 障害対応（アラートからの導線） |
