import { Users } from "lucide-react";

export default function KgsSvcCoachingSection() {
  const items = [
    "参加者が自ら安全行動を言語化し、チームで共有することで定着しやすい",
    "ファシリテーターは進行と安全な対話の型を担保",
    "「正解押し付け」ではなく、現場ルールと整合する改善行動に接続",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-svc-coach-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-svc-coach-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          コーチング型で進める理由
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <Users className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]" aria-hidden />
              <span>{t}</span>
            </li>
          ))}
        </ul>
        <div className="mt-10 border border-[#E4E4E7] bg-[#FAFAF9] p-5">
          <p className="text-left text-sm font-semibold text-[#18181B]">
            進行の透明性・説教にしない方針（信頼の置き場所）
          </p>
          <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B]">
            進行は透明性重視で、ブラックボックスな「独自ノウハウ」だけにしません。運転者を貶めず、改善に繋がる対話を守ることを、講習設計とファシリテーションの両面で優先します。
          </p>
        </div>
      </div>
    </section>
  );
}
