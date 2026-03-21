export default function KgsAboutPageHeaderSection() {
  const items = [
    "鹿児島市周辺の企業向けに、交通安全教育・講習を提供する一人事業（正式表記は要確認）",
    "全国規模の大量販売ではなく、担当者が説明しやすい情報と無理のない導入を重視",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-about-header-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="kgs-about-header-h1"
          className="text-left text-3xl font-bold tracking-tight text-[#18181B] md:text-4xl"
        >
          事業について
        </h1>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
