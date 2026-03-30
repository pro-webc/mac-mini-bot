# claude_final 選択バグ — Manus に拒否文・断片のみ渡る問題

- **発生案件**: #16878（STANDARD）、#16536（STANDARD）
- **発生日**: 2026-03-30
- **影響**: STANDARD/ADVANCE マルチページ案件で、下層ページのセクション数が構成案の 30〜70% に激減。Manus 生成画像も不足

## 問題の詳細

STANDARD パイプラインの手順7-4（chat6 の4回目メッセージ）で Claude CLI のコンテキスト圧縮が発生し、
step_7_4 の出力が拒否文（「No file system tools…」等）や差分のみになるケースが多発。

- #16878: step_7_3 = 123KB（正常 TSX）、step_7_4 = 911B（拒否文）
- #16536: step_7_3 = 140KB（正常 TSX）、step_7_4 = 38KB（差分のみ）

## 根本原因

`standard_cp_claude_manual.py` の `claude_final` 選択ロジック（旧コード）:

```python
raw_7_5 = (outs.step_7_5 or "").strip()
if raw_7_5 and has_tsx_content(raw_7_5):
    claude_final = raw_7_5
else:
    claude_final = (outs.step_7_4 or "").strip() or outs.step_7_3
```

`has_tsx_content` チェックが `step_7_5` にのみ適用され、`step_7_4` には適用されていなかった。
`step_7_5` が TSX でない → `step_7_4` が非空（拒否文でも truthy）→ `step_7_3` に到達しない。

同一パターンが `advance_cp_claude_manual.py` にも存在（`step_7_3` のチェック欠如）。

さらに、step_7_5 の入力に壊れた step_7_4 出力がそのまま渡されるため、step_7_5 も連鎖的に失敗。

## 実施した修正

### 1. `modules/standard_cp_claude_manual.py`

- **step_7_5 入力の改善**: step_7_4 が `has_tsx_content` を満たさない場合、step_7_3 を 7-5 にフィードバック
- **claude_final 選択**: 全候補（7_5 → 7_4 → 7_3）に `has_tsx_content` チェックを適用。最初に合格した出力を採用
- 選択結果をログ出力（`claude_final を step_7_X から選択 (chars=N)`）

### 2. `modules/advance_cp_claude_manual.py`

- 同じパターンで全候補（7_4 → 7_3 → 7_2）に `has_tsx_content` チェックを適用

### 3. `modules/basic_cp_claude_manual.py`

- `step_7_3` を直接使用しておりフォールバックチェーンなし → 修正不要

## 効果の予測

- #16878 相当のケース: Manus に渡るソースが 827B（拒否文）→ 123KB（フル TSX）に回復
- #16536 相当のケース: 22KB（ContactPage 断片）→ 140KB（フルサイト TSX）に回復
- 構成案のセクション数がコード化された状態で Manus に渡るため、リファクタ後のセクション維持率が大幅改善

## 次のアクション

- 修正後の次回 STANDARD 案件で、ログに `claude_final を step_7_X から選択` が出力されることを確認
- step_7_4 が失敗して step_7_3 にフォールバックした場合、最終サイトのセクション数を構成案と突合
- Manus 側でもセクション省略する傾向（原因2）は残存。重症度は低いが、別途プロンプト強化を検討
