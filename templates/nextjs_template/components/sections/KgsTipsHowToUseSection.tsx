export default function KgsTipsHowToUseSection() {
  const items = [
    "冒頭30秒：今日の安全目標を一言で共有",
    "1問：昨日の運転でうまくいった行動は？",
    "1問：明日から試す小さな改善は？",
    "注意：個人攻撃に繋がる言い回しは避ける（運営ガイド）",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-tips-how-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-tips-how-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          社内共有の使い方（テンプレ）
        </h2>
        <ol className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t, i) => (
            <li key={t} className="flex gap-3">
              <span className="font-bold text-[#1D4ED8] tabular-nums">
                {i + 1}.
              </span>
              <span>{t}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
