import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TshServiceValueAxesSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="value-axes-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="value-axes-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          支援の考え方：対話と可視化
        </h2>
        <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_1fr] lg:items-start">
          <div>
            <h3 className="text-lg font-semibold text-[#1c1917]">
              机上講義との違い
            </h3>
            <p className="mt-3 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
              講義は知識の土台には有効です。一方で、運転は状況判断の連続であり、座学だけでは個人差が残りやすい領域があります。TS-hubは、短時間でも参加者が「自分の言葉で言える」状態をつくる進行を重視します。
            </p>
            <h3 className="mt-8 text-lg font-semibold text-[#1c1917]">
              コーチング型セッションの進行イメージ
            </h3>
            <ul className="mt-3 flex list-disc flex-col gap-2 pl-5 text-left text-base leading-[1.7] text-[#1c1917]">
              <li>問いかけは結論押し付けではなく、具体行動に落とす方向づけ</li>
              <li>他者の事例から気づく時間を必ず確保</li>
              <li>管理者は“正解提示”より“対話の型”を持ち帰る</li>
            </ul>
            <p className="mt-4 text-sm text-[#57534e]">
              進行は貴社の文化に合わせて調整します。
            </p>
          </div>
          <div>
            <ImagePlaceholder
              aspectClassName="aspect-[4/3]"
              description="会議室のホワイトボード前で、参加者が付箋を並べている手元クローズアップ。顔は識別しにくい角度。対話と整理を連想。影は付けず、フラットな自然光。"
            />
            <h3 className="mt-10 text-lg font-semibold text-[#1c1917]">
              走行評価とデータの見せ方（概念）
            </h3>
            <p className="mt-3 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
              一般道路のコースを自社車で走行し、GPS等の情報を材料に、急ハンドルや急加減速などの傾向を整理します。目的はランキングではなく、本人が納得して改善方針を持てることです。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
