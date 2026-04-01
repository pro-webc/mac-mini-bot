# 自動スコアリング設計（Phase A）

## 目的

生成サイトの品質を**定量的・再現可能**に評価する基盤を構築する。これにより、フィードバックループ（Phase B）・可観測性（Phase D）・知識蓄積（Phase E）の全てが成立する。

---

## 評価の全体像

```
生成サイト（output/sites/<name>/）
    │
    ├─→ [技術検証] ビルド・Lint・ページ数 ─────────→ technical_score
    │
    ├─→ [構造検証] セクション・CTA・ナビ解析 ──────→ structural_score
    │
    ├─→ [スクリーンショット] Playwright 撮影 ──┐
    │                                          ├─→ [LLM 評価] → design_score
    ├─→ [ヒアリング原文] hearing_body ─────────┤
    │                                          ├─→ [LLM 評価] → content_score
    └─→ [LLM 出力] llm_steps/ ────────────────┘
                                                        │
                                                        ▼
                                               evaluation/scores.json
```

---

## 評価軸の定義

### 1. 技術品質スコア（technical_score）

**完全自動・決定的。LLM 不要。**

| チェック項目 | 合格条件 | 重み |
|-------------|---------|------|
| ビルド成功 | `npm run build` が exit 0 | 必須（0 点ならスコア全体 0） |
| ページ数一致 | `page.tsx` 数 = 契約ページ数 | 必須 |
| TypeScript エラー | `tsc --noEmit` エラー 0 | 高 |
| 画像パス有効性 | `src` 属性が `/public/` 内の実ファイルを参照 | 中 |
| コンソールエラー | Playwright でページロード時のコンソールエラー 0 | 中 |
| Lighthouse パフォーマンス | スコア 70 以上 | 低（参考値） |

**計算方法**: 必須項目が不合格なら 0 点。それ以外は重み付き加算（0〜100）。

### 2. 構造適合スコア（structural_score）

**自動解析 + ルールベース。LLM 不要。**

| チェック項目 | 検出方法 | 合格条件 |
|-------------|---------|---------|
| ヒーローセクション存在 | 最初の `<section>` or ヒーロー CSS クラス | 全ページに存在 |
| CTA ボタン配置 | `<a>` or `<button>` with CTA テキストパターン | ヒーロー・フッター付近に存在 |
| ナビゲーション | `<nav>` 要素の存在と内部リンク数 | 多ページサイトで全ページリンクあり |
| フッター | `<footer>` 要素の存在 | 全ページに存在 |
| レスポンシブ | Tailwind ブレークポイント (`md:`, `lg:`) の使用率 | 主要セクションで使用 |
| 法的情報 | プライバシーポリシー・特商法のリンク or モーダル | 存在する |

**計算方法**: 項目ごとに pass/fail → 合格率（0〜100）。

### 3. デザイン品質スコア（design_score）

**スクリーンショット → マルチモーダル LLM 評価。**

**撮影仕様:**

| パラメータ | 値 |
|-----------|---|
| ビューポート | 1280x800 (PC)、375x812 (SP) |
| 撮影対象 | フルページスクリーンショット |
| フォーマット | PNG |
| 保存先 | `evaluation/screenshots/` |

**LLM 評価プロンプトの評価項目:**

| 項目 | 配点 | 判定基準 |
|------|------|---------|
| 視覚的一貫性 | 20 | カラーパレット・フォント・余白が統一されているか |
| 階層の明確さ | 20 | 見出し→本文→CTAの視線誘導が成立しているか |
| 余白と密度 | 20 | 詰まりすぎ・スカスカがないか |
| 画像とテキストの調和 | 20 | プレースホルダーが不自然でないか、画像サイズが適切か |
| 全体印象 | 20 | プロが作ったサイトに見えるか |

**出力形式**: JSON（各項目のスコア + 理由テキスト）

### 4. コンテンツ品質スコア（content_score）

**LLM テキスト評価。**

| 項目 | 配点 | 判定基準 |
|------|------|---------|
| ヒアリング反映度 | 30 | 顧客の要望・強み・ターゲットが反映されているか |
| 文章の自然さ | 20 | 不自然な日本語・AI 臭さがないか |
| CTA の説得力 | 20 | 行動喚起が具体的で魅力的か |
| 情報の過不足 | 15 | 必要情報の欠落・不要な情報の混入がないか |
| 誤字・表記ゆれ | 15 | 固有名詞・専門用語の正確性 |

**入力**: ヒアリング原文 + 生成サイトの全テキスト（HTML から抽出）

---

## モジュール構成

```
modules/
└── evaluation/
    ├── __init__.py
    ├── evaluator.py            ← 統括: 全評価軸を呼び出してスコア集約
    ├── technical_checker.py    ← ビルド・Lint・ページ数
    ├── structural_checker.py   ← セクション・CTA・ナビ解析
    ├── screenshot_capture.py   ← Playwright スクリーンショット撮影
    ├── design_evaluator.py     ← スクリーンショット → LLM 評価
    ├── content_evaluator.py    ← テキスト抽出 → LLM 評価
    └── scoring.py              ← スコア計算・重み付き集約
```

---

## 出力フォーマット

### `evaluation/scores.json`

```json
{
  "record_number": "12345",
  "partner_name": "サンプル株式会社",
  "contract_plan": "STANDARD",
  "evaluated_at": "2026-03-31T14:00:00+09:00",
  "prompt_version": "v2.3",
  "scores": {
    "technical": 95,
    "structural": 80,
    "design": 72,
    "content": 68,
    "overall": 76
  },
  "details": {
    "technical": {
      "build_success": true,
      "page_count_match": true,
      "typescript_errors": 0,
      "console_errors": 0,
      "lighthouse_performance": 82
    },
    "structural": {
      "hero_present": true,
      "cta_placed": true,
      "navigation_complete": false,
      "footer_present": true,
      "responsive_usage": 0.85,
      "legal_info": true
    },
    "design": {
      "visual_consistency": 15,
      "hierarchy_clarity": 16,
      "spacing_density": 14,
      "image_text_harmony": 12,
      "overall_impression": 15,
      "reasoning": "..."
    },
    "content": {
      "hearing_reflection": 22,
      "text_naturalness": 14,
      "cta_persuasion": 12,
      "info_completeness": 10,
      "accuracy": 10,
      "reasoning": "..."
    }
  }
}
```

### `evaluation/screenshots/`

```
evaluation/screenshots/
├── pc_full.png          ← 1280x800 フルページ
├── sp_full.png          ← 375x812 フルページ
├── pc_above_fold.png    ← ファーストビュー
└── sp_above_fold.png    ← SP ファーストビュー
```

---

## パイプラインへの組み込み

既存の Phase 5 の**後**に Phase 6 として追加する。既存フェーズは変更しない。

```python
# main.py WebsiteBot.process_case() への追加イメージ

def process_case(self, case):
    # 既存 Phase 1-5（変更なし）
    hearing_bundle, work_branch, plan_info = self._phase1_hearing_and_branch(case)
    llm_result, spec = self._phase2_text_llm(...)
    site_dir = self._phase3_prepare_site(...)
    self._phase4_build(...)
    deploy_url = self._phase5_deploy(...)

    # 新規 Phase 6: 評価
    if EVALUATION_ENABLED:
        scores = self._phase6_evaluate(
            record_number=case.record_number,
            site_dir=site_dir,
            deploy_url=deploy_url,
            hearing_body=hearing_bundle.hearing_body,
            contract_plan=plan_info,
        )
        log.info(f"評価完了: overall={scores['overall']}")
```

---

## 実装の優先順

| 順番 | 対象 | 理由 |
|------|------|------|
| 1 | `technical_checker.py` | ルールベースで即実装可能。既存の Phase 4 チェックを拡張するだけ |
| 2 | `structural_checker.py` | HTML パースのみ。LLM 不要 |
| 3 | `screenshot_capture.py` | Playwright 導入。デザイン評価の前提 |
| 4 | `design_evaluator.py` | マルチモーダル LLM。プロンプト設計が必要 |
| 5 | `content_evaluator.py` | テキスト LLM。ヒアリングとの照合ロジック |
| 6 | `evaluator.py` + `scoring.py` | 全軸統合。重み調整 |

---

## 設定

```bash
# .env に追加
EVALUATION_ENABLED=true
EVALUATION_SCREENSHOT_ENABLED=true
EVALUATION_LLM_MODEL=claude-sonnet-4-6       # 評価用は Sonnet で十分
EVALUATION_SCORE_THRESHOLD=60                  # この値未満で警告
```

---

## 関連ドキュメント

| 文書 | 役割 |
|------|------|
| [EVOLUTION_ROADMAP.md](./EVOLUTION_ROADMAP.md) | 全体ロードマップ |
| [FEEDBACK_LOOP.md](./FEEDBACK_LOOP.md) | スコアを使った改善ループ（Phase B） |
| [OUTPUT_LAYOUT.md](./OUTPUT_LAYOUT.md) | 既存トレース構造（評価の入力） |
| [TECH_REQUIREMENTS.md](./TECH_REQUIREMENTS.md) | 品質ガードレール（評価基準の根拠） |
