/**
 * 技術土台のみのスタブ。セクション・ナビ・デザインは仕様書に基づき別途実装する。
 * セクション単位のコンポーネントは components/sections/ に配置すること。
 */
export default function Page() {
  return (
    <main>
      <div className="p-6">
        <p className="text-sm text-neutral-600">
          このリポジトリは Next.js (App Router) の技術土台のみです。
          app/page.tsx・components/sections/* は仕様書・LLM により実装してください。
        </p>
      </div>
    </main>
  )
}
