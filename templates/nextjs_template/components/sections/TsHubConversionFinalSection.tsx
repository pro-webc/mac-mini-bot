import { CalendarCheck2, ClipboardList, Video } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function TsHubConversionFinalSection() {
  return (
    <section
      className="bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="final-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="final-cta-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          まずは状況を聞かせてください
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
            <ClipboardList className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              相談内容を事前に整理できるフォーム
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
            <CalendarCheck2 className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              日程調整はTimeRex等の外部ツール（クライアント側アカウント想定）へ誘導
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
            <Video className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              オンサイト／オンライン等の提供形態は要ヒアリングで確定
            </p>
          </li>
        </ul>
        <div className="mt-10">
          <CtaButton href="/contact">
            <CalendarCheck2 className="h-5 w-5" aria-hidden />
            無料相談を予約する
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
