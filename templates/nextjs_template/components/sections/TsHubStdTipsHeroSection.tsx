export default function TsHubStdTipsHeroSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-14 md:py-16"
      aria-labelledby="tips-hero-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="tips-hero-heading"
          className="text-3xl font-bold leading-tight text-[#0F172A] md:text-4xl"
        >
          一口アドバイス
        </h1>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          朝礼やミーティングで、そのまま読み上げられる短い話題をまとめています。週次で更新できる型を前提にしています。
        </p>
      </div>
    </section>
  );
}
