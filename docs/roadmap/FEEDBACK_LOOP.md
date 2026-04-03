# フィードバックループ設計（Phase B）— 部分実装済み

## 目的

[自動スコアリング](./AUTO_SCORING.md)の評価結果を起点に、**プロンプト改善の提案・検証・適用**を自動化する。人間が output を見てプロンプトを直す現在のサイクルを、AI が自律的に回せるようにする。

## 実装状況（2026-04-03）

**Slack 修正指示をトリガーにした自己改善が稼働中。** Phase A（自動スコアリング）が未完成でも、Slack の修正指示を評価信号として利用し、プロンプトの自律的改善サイクルを回している。

### 実装済みモジュール

| モジュール | 役割 |
|-----------|------|
| `modules/correction_flow.py` | 修正フロー全体のオーケストレーション |
| `modules/self_improvement.py` | プロンプト自己改善エンジン |
| `modules/slack_client.py` | Slack チャンネルからの修正指示取得 |

### 実装済みフロー

```
Slack 修正指示
  → [1.5] 構造化抽出（雑談除去、カテゴリ分類、優先度判定）
  → [2] 原因調査（浅い: 200文字プレビュー）
  → [3] git clone
  → [4] Claude CLI 修正（技術要件 technical_spec_prompt_block.txt 適用）
  → [4.5] 画像修正（image カテゴリ → Manus に委譲）
  → [5] git push
  → [6] 修正記録保存
  → [7] 自己改善（フルトレース + プロンプト全文で深い調査 → 改善適用 → Git commit）
  → [8] Slack 報告（原因 → 改善内容 → 修正内容）
  → スプレッドシート「デモサイト制作完了」更新（レコード番号で行再照合）
```

### パイプラインマニフェスト

`self_improvement.py` に全 4 プランタイプのトレースステップ番号→プロンプトファイル対応表を定義:
- `basic_lp`: 12 ステップ
- `basic`: 11 ステップ
- `standard`: 17 ステップ
- `advance`: 16 ステップ

### LLM トレース記録

修正フローの全 LLM 呼び出しを生成工程と同じ `output/<record>/llm_steps/` に記録:
- `correction_extract_instructions` — Slack 指示の構造化抽出
- `correction_investigation` — 原因調査
- `correction_site_fix` — サイト修正
- `correction_manus_image` — Manus 画像修正

### 未実装（元の Phase B 設計のうち）

- A/B 比較実行
- スコアベースの低品質検出（Phase A 依存）
- プロンプトバージョニング（`prompt_version.json`）
- 効果の統計的検定

---

## フィードバックループの全体フロー

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
  ┌──────────────────────┐                                │
  │ 1. スコア収集         │                                │
  │    scores.json 蓄積   │                                │
  └──────────┬───────────┘                                │
             │                                            │
             ▼                                            │
  ┌──────────────────────┐                                │
  │ 2. 低スコア検出       │                                │
  │    閾値以下の軸を特定  │                                │
  └──────────┬───────────┘                                │
             │                                            │
             ▼                                            │
  ┌──────────────────────┐                                │
  │ 3. 原因ステップ特定   │                                │
  │    llm_steps/ を遡及  │                                │
  └──────────┬───────────┘                                │
             │                                            │
             ▼                                            │
  ┌──────────────────────┐                                │
  │ 4. 改善案生成         │                                │
  │    プロンプト修正提案  │                                │
  └──────────┬───────────┘                                │
             │                                            │
             ▼                                            │
  ┌──────────────────────┐                                │
  │ 5. A/B 実行          │                                │
  │    同一入力で比較実行  │                                │
  └──────────┬───────────┘                                │
             │                                            │
             ▼                                            │
  ┌──────────────────────┐                                │
  │ 6. 効果判定           │                                │
  │    スコア差の統計検定  │───→ 採用 → プロンプト更新 ─────┘
  └──────────────────────┘
             │
             └───→ 棄却 → 別の改善案で再試行
```

---

## 各ステップの詳細

### 1. スコア収集と傾向分析

**入力**: `output/*/evaluation/scores.json` の集合

| 分析対象 | 方法 | アクション |
|---------|------|----------|
| 軸別平均スコアの推移 | 直近 N 件の移動平均 | 下降トレンドを検知 |
| プラン別スコア分布 | BASIC LP / STANDARD 等で分割 | 特定プランの弱点を特定 |
| 低スコア案件の共通点 | 業種・ヒアリング長・要件パターン | 苦手パターンを特定 |

### 2. 低スコア検出

```python
# 閾値判定のイメージ
THRESHOLDS = {
    "technical": 90,   # 技術品質は高水準を要求
    "structural": 75,
    "design": 65,
    "content": 65,
    "overall": 70,
}

def detect_low_scores(scores: dict) -> list[str]:
    """閾値未満の軸を返す"""
    return [axis for axis, threshold in THRESHOLDS.items()
            if scores.get(axis, 0) < threshold]
```

### 3. 原因ステップ特定

低スコアの評価軸から、責任を持つ LLM ステップを逆引きする。

| 評価軸 | 主な責任ステップ | 根拠 |
|--------|----------------|------|
| technical | step_8_1〜8_3（コード生成） | ビルドエラー・型エラーの直接原因 |
| structural | step_2（ページ構成）, step_4（ワイヤーフレーム） | セクション設計の根本 |
| design | step_5（デザインパレット）, step_7（デザイン仕様） | 色・レイアウト・余白の決定 |
| content | step_1_1（ヒアリング抽出）, step_3（コンセプト） | 情報抽出と表現方針 |

**特定手順:**
1. 低スコア軸に対応するステップ群を候補に挙げる
2. 各候補ステップの `input.md` / `output.md` を LLM に読ませる
3. 「この出力のどの部分が最終成果物の品質低下に寄与しているか」を分析

### 4. 改善案生成

LLM に以下を入力して改善案を生成する:

```
入力:
  - 現在のプロンプト（config/prompts/<plan>_manual/step_X.txt）
  - そのステップの出力（output/<record>/llm_steps/NNN/output.md）
  - 評価結果（evaluation/scores.json の該当軸）
  - 品質ガードレール（config/prompts/common/technical_spec_prompt_block.txt）

出力:
  - 修正後プロンプト（差分形式）
  - 修正理由
  - 期待されるスコア改善の仮説
```

**改善案の保存先:**

```
output/<record>/improvement/
├── proposal_001.json
│   ├── target_step: "step_5"
│   ├── target_file: "config/prompts/basic_lp_manual/step_5.txt"
│   ├── diff: "..."
│   ├── reasoning: "デザインパレットの指示が曖昧..."
│   └── hypothesis: "design_score が +10 改善する見込み"
└── proposal_002.json
```

### 5. A/B 実行

同一のヒアリング入力に対して、元のプロンプトと改善プロンプトで並行実行する。

**実行方式:**

| 方式 | 説明 | 適用場面 |
|------|------|---------|
| **リプレイ方式** | 過去案件の `llm_steps/` 入力を再利用 | コスト最小。特定ステップのみ再実行 |
| **フルラン方式** | 新規案件で両プロンプトを並行実行 | 最も正確。ただし 2 倍のコスト |

**リプレイ方式の詳細:**

```
1. 過去案件の step_N の input.md を取得
2. 元のプロンプトで実行 → output_A.md → 評価 → score_A
3. 改善プロンプトで実行 → output_B.md → 評価 → score_B
4. score_B - score_A を改善効果として記録
```

### 6. 効果判定と適用

| 条件 | アクション |
|------|----------|
| score_B - score_A >= +5（複数案件で一貫） | **採用**: プロンプトファイルを更新 |
| -2 < diff < +5 | **保留**: サンプル追加で再検証 |
| score_B - score_A <= -2 | **棄却**: 改善案を破棄、別案を試行 |

---

## プロンプトバージョニング

### バージョン管理方式

プロンプトファイルは Git で管理されているため、**Git タグ + メタデータファイル**で実験を追跡する。

```
config/prompts/
├── prompt_version.json           ← 現在のバージョンと変更履歴
├── basic_lp_manual/
│   ├── step_5.txt                ← 現行版
│   └── ...
└── experiments/                  ← A/B 実験用の差分保存
    └── exp_20260331_design/
        ├── experiment.json       ← 実験メタデータ
        ├── step_5.txt            ← 改善版プロンプト
        └── results.json          ← A/B 結果
```

### `prompt_version.json`

```json
{
  "current_version": "v2.3",
  "last_updated": "2026-03-31",
  "changelog": [
    {
      "version": "v2.3",
      "date": "2026-03-31",
      "changes": ["step_5: デザインパレットの色指定を具体化"],
      "experiment_id": "exp_20260331_design",
      "score_impact": { "design": "+8", "overall": "+3" }
    }
  ]
}
```

---

## 人間承認ゲート

Phase B の初期段階では、改善案の適用前に人間が確認する。

| 段階 | 自動化範囲 | 人間の関与 |
|------|----------|----------|
| **Stage 1** | スコア収集〜改善案生成まで自動 | 改善案のレビュー + A/B 実行の承認 |
| **Stage 2** | A/B 実行・効果判定まで自動 | プロンプト更新の承認のみ |
| **Stage 3** | 全自動（効果が +5 以上かつ副作用なし） | 週次レポートの確認のみ |

---

## モジュール構成

```
modules/
└── feedback/
    ├── __init__.py
    ├── trend_analyzer.py        ← スコア傾向分析・低スコア検出
    ├── root_cause_finder.py     ← 低スコア → 原因ステップ特定
    ├── improvement_proposer.py  ← 改善案生成
    ├── ab_runner.py             ← A/B リプレイ実行
    ├── effect_judge.py          ← 効果判定・採用/棄却
    └── prompt_versioner.py      ← バージョン管理・差分適用
```

---

## 関連ドキュメント

| 文書 | 役割 |
|------|------|
| [EVOLUTION_ROADMAP.md](./EVOLUTION_ROADMAP.md) | 全体ロードマップ |
| [AUTO_SCORING.md](./AUTO_SCORING.md) | 評価基盤（Phase A、本設計の前提） |
| [OUTPUT_LAYOUT.md](../pipeline/OUTPUT_LAYOUT.md) | llm_steps/ 構造（リプレイの入力） |
| [LLM_PIPELINE.md](../pipeline/LLM_PIPELINE.md) | 多段チェーン設計（改善対象の理解） |
| [PIPELINE_TESTING.md](../pipeline/PIPELINE_TESTING.md) | 既存の A/B 検証手順 |
