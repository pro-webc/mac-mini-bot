import { Calendar, Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import { EXTERNAL_SCHEDULER_BOOKING_URL } from "@/lib/schedulerUrl";

const outlineClass =
  "inline-flex min-h-[48px] min-w-[44px] w-full items-center justify-center gap-2 rounded-[12px] border-2 border-[#1D4ED8] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:border-[#1E40AF] hover:bg-[#F4F4F5] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] motion-safe:transition-colors sm:w-auto";

export default function KgsSvcCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-24"
      aria-labelledby="kgs-svc-cta-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-svc-cta-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          内容を自社向けに具体化したい方へ
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-relaxed text-[#18181B]">
          車両台数・対象ドライバー・実施頻度・課題のメモがあれば共有ください
        </p>
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            相談内容を送る
          </CtaButton>
          <a
            href={EXTERNAL_SCHEDULER_BOOKING_URL}
            target="_blank"
            rel="noopener noreferrer"
            className={outlineClass}
          >
            <Calendar className="h-5 w-5 shrink-0" aria-hidden />
            面談日程を選ぶ
          </a>
        </div>
      </div>
    </section>
  );
}
