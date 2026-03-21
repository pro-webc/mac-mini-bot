export default function TshServiceWhoForSection() {
  const bullets = [
    "業務車の運行が多く、白ナンバー中心でドライバー層が幅広い",
    "安全運転管理者が「伝える」負担が大きい",
    "教育は実施しているが、現場の行動変容が見えにくい",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="who-for-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="who-for-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          こんな組織さまに向いています
        </h2>
        <ul className="mt-8 flex flex-col gap-3">
          {bullets.map((t) => (
            <li
              key={t}
              className="border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
