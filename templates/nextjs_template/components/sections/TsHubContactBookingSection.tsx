import { Calendar } from "lucide-react";
import { EXTERNAL_SCHEDULER_BOOKING_URL } from "@/lib/schedulerUrl";

export default function TsHubContactBookingSection() {
  return (
    <section id="booking" className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Calendar className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              オンライン面談の日程調整
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              外部の予約ツールに接続します。URLが未設定の場合は、返信メールでご案内します。フォーム送信後でもご利用いただけます。
            </p>
            <a
              href={EXTERNAL_SCHEDULER_BOOKING_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-6 inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#1D4ED8] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:bg-[#EFF6FF] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            >
              <Calendar className="h-5 w-5 shrink-0" aria-hidden />
              日程を選ぶ
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
