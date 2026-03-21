import { Sparkles } from "lucide-react";

const bullets = [
  "年度初めの安全教育の立ち上げ",
  "新入社員・配属時の安全意識の前振り",
  "白ナンバー中心の業務車運用の見直し議論の土台づくり",
];

export default function TsHubServicesUseCasesSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Sparkles className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
            こんな場面で選ばれます
          </h2>
        </div>
        <ul className="mt-8 grid gap-3 md:grid-cols-3">
          {bullets.map((t) => (
            <li
              key={t}
              className="border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-left text-sm leading-relaxed text-[#18181B] md:text-base"
            >
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
