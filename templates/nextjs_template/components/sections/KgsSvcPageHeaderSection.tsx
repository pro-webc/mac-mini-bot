export default function KgsSvcPageHeaderSection() {
  const items = [
    "集合・オンライン併用など、企業の運用に合わせて設計（詳細は要確認）",
    "安全会議・朝礼運用と連動する使い方も提案",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-svc-header-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="kgs-svc-header-h1"
          className="text-left text-3xl font-bold tracking-tight text-[#18181B] md:text-4xl"
        >
          講習・支援内容
        </h1>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <span className="font-semibold text-[#1D4ED8]">・</span>
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
