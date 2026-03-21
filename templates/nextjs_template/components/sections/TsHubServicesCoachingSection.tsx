import { ListChecks } from "lucide-react";

const bullets = [
  "目的が明確なワークと振り返りをセットにします。",
  "参加者が『うちの会社では』と接続できる時間を確保します。",
  "集合・オンラインの切り分けは、学習目標と制約から提案します。",
];

export default function TsHubServicesCoachingSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          コーチング型グループ研修
        </h2>
        <ul className="mt-8 space-y-3">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4"
            >
              <ListChecks
                className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <span className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                {t}
              </span>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-left text-sm text-[#52525B]">
          内容は事前ヒアリングの結果により調整します。
        </p>
      </div>
    </section>
  );
}
