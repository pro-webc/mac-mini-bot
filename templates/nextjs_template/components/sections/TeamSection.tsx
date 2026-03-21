const members = [
  { initial: "A", role: "代表（仮）", note: "顔写真・肩書きは確定後に掲載予定。" },
  { initial: "B", role: "現場担当（仮）", note: "自己紹介文と動画で雰囲気を補足予定。" },
  { initial: "C", role: "事務・受付（仮）", note: "連絡窓口の役割分担は運用確定待ち。" },
];

export default function TeamSection() {
  return (
    <section className="bg-[#FFFFFF] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          チーム・担当
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          写真が未確定の間はイニシャルと役割のテキストカードでご案内します。
        </p>
        <ul className="mt-10 grid gap-6 md:grid-cols-3">
          {members.map((m) => (
            <li
              key={m.initial + m.role}
              className="flex flex-col rounded-[20px] border border-[#E2E8F0] bg-[#F8FAFC] p-6"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#0284C7] text-2xl font-bold text-white">
                {m.initial}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-[#0F172A]">{m.role}</h3>
              <p className="mt-2 flex-1 text-left text-sm leading-relaxed text-[#475569]">
                {m.note}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
