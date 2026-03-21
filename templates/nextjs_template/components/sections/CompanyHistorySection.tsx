const milestones = [
  { period: "個人事業時代", note: "詳細時期はクライアント確定値に差し替え予定。" },
  { period: "前年度6月", note: "法人化（創立から1年未満の案内あり）" },
  { period: "現在", note: "Web サイトを通じたご相談窓口を拡充中" },
];

export default function CompanyHistorySection() {
  return (
    <section className="bg-[#F8FAFC] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          沿革
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          個人事業から法人化に至る経緯を、確定情報に基づき追記します。以下はプレースホルダの年表です。
        </p>
        <ol className="mt-10 space-y-4">
          {milestones.map((m, i) => (
            <li
              key={m.period}
              className="flex gap-4 rounded-[16px] border border-[#E2E8F0] bg-[#FFFFFF] p-5"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#0EA5E9] text-sm font-bold text-white">
                {i + 1}
              </span>
              <div>
                <p className="text-base font-semibold text-[#0F172A]">{m.period}</p>
                <p className="mt-2 text-left text-sm leading-relaxed text-[#475569]">
                  {m.note}
                </p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
