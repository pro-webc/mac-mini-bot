# プラン共通の技術要件

実装・仕様書生成の際は `config.config.COMMON_TECHNICAL_SPEC` および `get_common_technical_spec_prompt_block()` と同一内容を遵守してください。

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

- **Unsplash 禁止**
- **実画像ファイルは配置しない**
- 画像プレースホルダー枠 + 詳細説明で意図を示す
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
