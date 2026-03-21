export default function KgsHomeAudiencePainSection() {
  const items = [
    "朝礼がマンネリ化し、注意が空回りしがち",
    "教育の効果が見えず、上司への説明が難しい",
    "現場の実態に合わない一般論になりがち",
    "オンライン最適化の判断材料が欲しい",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-home-pain-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-pain-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          こんな手応えのなさ、ありませんか？
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="border-l-4 border-[#1D4ED8] pl-4">
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
