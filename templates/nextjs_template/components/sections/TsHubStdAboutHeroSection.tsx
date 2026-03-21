export default function TsHubStdAboutHeroSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-14 md:py-16"
      aria-labelledby="about-hero-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="about-hero-heading"
          className="text-3xl font-bold leading-tight text-[#0F172A] md:text-4xl"
        >
          講師・事業について
        </h1>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          鹿児島市周辺の法人向けに、交通安全教育に集中して支援します。
        </p>
      </div>
    </section>
  );
}
