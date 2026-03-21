import { Calendar, Mail } from "lucide-react";
import { EXTERNAL_SCHEDULER_BOOKING_URL } from "@/lib/schedulerUrl";

export default function KgsContactMethodsSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-contact-methods-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-contact-methods-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          連絡方法
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          <li className="flex gap-3">
            <Mail className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]" aria-hidden />
            <span>フォーム：推奨</span>
          </li>
          <li className="flex gap-3">
            <Calendar className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]" aria-hidden />
            <span>
              予約ツール：面談の日程確定用（
              <a
                href={EXTERNAL_SCHEDULER_BOOKING_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-[#1D4ED8] underline-offset-4 hover:text-[#1E40AF] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
              >
                外部サービスへ
              </a>
              ）
            </span>
          </li>
          <li>電話：（公開可否が確定した場合のみ表示）</li>
        </ul>
      </div>
    </section>
  );
}
