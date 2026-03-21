export default function KgsMeasDeliverablesSection() {
  const items = [
    "集合研修の進行資料（要確認）",
    "振り返り用の問いかけリスト",
    "評価サマリ（形式はヒアリングで確定）",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-meas-deliver-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-meas-deliver-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          成果物イメージ（例）
        </h2>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-2">
              <span className="text-[#1D4ED8]" aria-hidden>
                ■
              </span>
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
