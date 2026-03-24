# 技術要綱（スタック・実装制約）

情報は次の経路で現れます。

1. **各マニュアルの手順 7〜8 付近**に繰り返し書かれる短い箇条書き（Gemini への直接プロンプト）。
2. **`config/prompts/common/technical_spec_prompt_block.txt`** — 読み取りは `config.prompt_settings.get_technical_spec_prompt_block()`。内容は**全プラン共通の長文ルール**。
3. **`config.config.COMMON_TECHNICAL_SPEC`** — 辞書。`apply_common_technical_to_spec` で仕様 dict の `technical_spec.common_requirements` にマージ。
4. **`output/sites/.../TECH_REQUIREMENTS.md`** — `SiteGenerator._write_tech_requirements` が (2) と同じテキストを書き出し（人間・レビュー・push 用。Gemini チェーンには自動連結されない点に注意）。

---

## `technical_spec_prompt_block.txt` の構造（要約）

| ブロック | 内容 |
|----------|------|
| ソースの正本 | パイプライン上の Gemini 出力が完成形の正本。デモ素片に依存しない。 |
| 技術要件 | Next.js App Router, React, Tailwind。1 セクション≈1 コンポーネント。@import は CSS 最上部。図表はマークアップ。Lucide / SNS は Simple Icons。存在しないアイコン名禁止。 |
| 画像 | Unsplash 禁止。ヒーローは必ず画像。ビジュアル最低 3 意図箇所。最終リファクタで `next/image` + `public/images/`。ImagePlaceholder の扱い。 |
| 地図 | 所在地は Google Maps 埋め込み。マップエリアに画像プレースホルダ禁止。対応エリア用の装飾画像禁止。 |
| 装飾 | `shadow-*`（box-shadow）禁止。 |
| スタイリング | design_spec 優先、テキスト色・CTA・タイポ・セクション間リズム・任意値の制限。 |
| UX | タップ 44px 目安、フォーム label、focus-visible、reduced-motion、ランドマーク、横スクロール回避。 |
| 表現 | Unicode 絵文字の禁止範囲と例外（ヒアリングに明示されたもののみ転記可）。 |

---

## `COMMON_TECHNICAL_SPEC`（辞書のキー）

`config/config.py` 参照。

- `stack`: framework / ui / styling  
- `architecture`: セクションコンポーネント、App Router  
- `css_rules`: `@import` 順序  
- `content_visualization`: 図表はコードで  
- `icons`: Lucide、SNS、プレースホルダ禁止  
- `images`: Unsplash 禁止、最終リファクタでの画像方針  
- `maps`: 埋め込み・禁止事項・ピン  
- `styling_policy`: Tailwind 前提、CSS 変数、テキスト色、ボタン状態  

---

## Manus オーケストレーション内の技術メモ

`orchestration_prompt.txt` の「CSS 実装時の必須ルール」:

- `@import` を先頭（コメントの後）
- `:root` / `@theme` / その他の順
- **Google Fonts は CSS @import ではなく `layout.tsx` の `<link>`**（リファクタ手順との整合）

`refactoring_instruction_handwork.txt` の技術要点:

- `next/image`・`next/link` 必須（`<img>` や onClick 遷移禁止）
- Client Component は `"use client"`、ページは原則 Server Component
- Hydration: 不正な HTML ネスト禁止、`suppressHydrationWarning` on `body`
- Tailwind v4 時は色等を `globals.css` の `@theme` に（設定として許容）
- `page.tsx` に className やレイアウト JSX を書かない等の**厳格ルール**

---

## LLM_PIPELINE.md との対応

- ボットは **ビルド失敗時にソースを自動修正しない**（`npm run build` は検証のみ）。
- サイト用画像の一括生成 API は本パイプラインからは呼ばない（Manus 側で nanobanana 等の指示がある）。
