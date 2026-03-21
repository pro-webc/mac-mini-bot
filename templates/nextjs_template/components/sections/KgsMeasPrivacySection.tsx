export default function KgsMeasPrivacySection() {
  const items = [
    "取得目的、保存期間、第三者提供の有無は契約前に文書で確認",
    "必要最小限の範囲で設計し、参加者への説明テンプレを用意（文言は確定後）",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-meas-privacy-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-meas-privacy-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          データと個人情報の扱い（方針）
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
