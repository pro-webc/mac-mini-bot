import Link from "next/link";
import { ChevronRight, GraduationCap, MonitorSmartphone, UserRound, Building } from "lucide-react";

const items = [
  { text: "集合研修（社内／会場）案", Icon: Building },
  { text: "オンサイト講習案", Icon: GraduationCap },
  { text: "個別コンサル／伴走案", Icon: UserRound },
  { text: "オンライン可否は要調整", Icon: MonitorSmartphone },
];

export default function TsServicePackagesSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="packages-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="packages-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          提供メニュー（名称・形式は確定後に確定）
        </h2>
        <ul className="mt-8 grid gap-4 sm:grid-cols-2">
          {items.map(({ text, Icon }) => (
            <li
              key={text}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5"
            >
              <Icon className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                {text}
              </p>
            </li>
          ))}
        </ul>
        <div className="mt-10">
          <Link
            href="/contact"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] hover:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
          >
            実施イメージを相談する
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
