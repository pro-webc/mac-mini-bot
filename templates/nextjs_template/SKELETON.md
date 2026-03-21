# 技術土台（スケルトン）

このディレクトリは **構成・コンテンツ・ブランドデザインを含まない** Next.js プロジェクトの最小構成です。

## 含まれるもの

- Next.js App Router + TypeScript + Tailwind + ESLint 依存（package.json）
- `app/layout.tsx` / `app/page.tsx`（page はスタブのみ）
- `app/globals.css`（`@import` 先頭・Tailwind ディレクティブのみ）
- `components/ImagePlaceholder.tsx` / `GoogleMapEmbed.tsx`（技術要件どおりの部品）
- `lib/ctaButtonClass.ts`（CTA 用 Tailwind クラス。実装 LLM が `design_spec` に合わせて `<<<FILE>>>` で上書き可能）
- `components/sections/`（空＋ README。セクションはここに追加）
- `TECH_REQUIREMENTS.md`（プラン共通の技術要項）

## 含めないもの（別途実装）

- ヘッダー・フッター・ナビの構成
- ヒーロー・サービス紹介などのセクション TSX
- カラーパレット・コンポーネントの見た目設計（仕様書・LLM で決定）

## 次のステップ

仕様書（`spec`）に基づき `app/page.tsx`・`components/sections/*`・必要なら `lib/*.ts` を生成・編集する。
