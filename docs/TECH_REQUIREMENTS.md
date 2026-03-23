# プラン共通の技術要件

実装・仕様書生成の際は `config.config.COMMON_TECHNICAL_SPEC` および `get_common_technical_spec_prompt_block()` と同一内容を遵守してください。  
LLM へ渡す文言の正本は **`config/prompts/common/technical_spec_prompt_block.txt`**（UTF-8 プレーンテキスト）です。

## 技術スタック

- Next.js (App Router), React, Tailwind CSS
- セクション単位でコンポーネント化（原則 1 セクション = 1 コンポーネント）

## CSS

- `@import`（Google Fonts 等）は **globals.css または `<style>` の最上部**（`:root` や他ルールより前）。違反するとビルドエラーになり得ます。

## 図表

- 図解・比較表は **画像ではなく** マークアップ + Tailwind で生成

## アイコン

- 基本: **Lucide React**
- SNS: **Simple Icons**（例: `react-icons/si`）
- アイコンを画像プレースホルダで代用しない

## 画像

- **Unsplash・外部ストック URL 禁止**（プロンプト正本どおり）
- **ヒーローには画像を用いる**（`next/image` + `public/images/` の静的ファイル。詳細は正本テキスト）
- マニュアル途中はプレースホルダー可。**最終リファクタ工程**で意図どおりのビジュアルに置き換える
- 画像上に載せるテキストはオーバーレイとして表示

## 地図・対応エリア

- 所在地: **Google Maps 埋め込み**。マップ領域に画像・プレースホルダ禁止
- 「対応エリア」用の画像・イラストは生成・配置とも禁止
- 所在地が明確な場合はピン付き地図

## スタイリング

- Tailwind を前提に実装
- CSS 変数を使う場合も要素ごとに色を明示
- `body` の色継承に頼らずテキスト要素ごとに色指定
- ボタンは hover / active / disabled 等、状態ごとに色を明示

## コピー・情報密度（概要）

- 構成案の【テキスト情報】を実装で要約・省略しない。Lorem 等のダミー本文をユーザー向けに出さない。
- 詳細は正本テキストの **【コピー・情報密度・完成度】** を参照。

## 没入感・現代UI（概要）

- 世界観の一貫性、セクションリズム、軽いインタラクション（`motion-safe:` / `prefers-reduced-motion`）。装飾の `shadow-*` 禁止は変わらない。
- 詳細は正本の **【没入感・世界観・現代的UI】** を参照。
