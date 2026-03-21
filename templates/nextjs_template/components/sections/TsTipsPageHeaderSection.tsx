export default function TsTipsPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="tips-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="tips-h1"
          className="text-left text-2xl font-bold text-[#18181B] md:text-3xl"
        >
          週1の一口アドバイス
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>朝礼・ミーティングでそのまま使える短いネタ</p>
          <p>専門用語は避け、現場語彙で書きます。</p>
        </div>
      </div>
    </section>
  );
}
