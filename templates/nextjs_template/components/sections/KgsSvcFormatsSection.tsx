export default function KgsSvcFormatsSection() {
  const items = [
    "オンサイト集合型：対話とワークを中心に進行",
    "オンライン併用：地理分散・時間制約への切り分け",
    "事前ヒアリング後のカスタム設計：対象職種・事故傾向・管理項目に合わせて構成調整",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-svc-formats-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-svc-formats-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          提供形態（例）
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
