import { Calendar, Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import { EXTERNAL_SCHEDULER_BOOKING_URL } from "@/lib/schedulerUrl";

const secondaryOnBrandClass =
  "inline-flex min-h-[48px] min-w-[44px] w-full items-center justify-center gap-2 rounded-[12px] border-2 border-[#FFFFFF]/70 bg-[#1E40AF] px-6 py-3 text-base font-semibold text-[#FFFFFF] transition-colors hover:border-[#FFFFFF] hover:bg-[#1e3a8a] active:bg-[#172554] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#FFFFFF] motion-safe:transition-colors sm:w-auto";

export default function KgsHomeFinalCtaSection() {
  const bullets = [
    "問い合わせ：内容・体制・希望日程のたたき台を送れる",
    "日程調整：外部予約ツール（例：タイムレックス等、アカウントは別途）へ",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#1D4ED8] py-16 md:py-24"
      aria-labelledby="kgs-home-final-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-final-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#FFFFFF] md:text-3xl"
        >
          まずは15分、現状と目的を整理しませんか？
        </h2>
        <ul className="mt-6 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#E4E4E7]">
          {bullets.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <CtaButton
            href="/contact"
            className="w-full justify-center border-2 border-[#FFFFFF]/80 !bg-[#172554] !text-[#FFFFFF] hover:!border-[#FFFFFF] hover:!bg-[#0f172a] focus-visible:!outline-[#FFFFFF] sm:w-auto"
          >
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            お問い合わせする
          </CtaButton>
          <a
            href={EXTERNAL_SCHEDULER_BOOKING_URL}
            target="_blank"
            rel="noopener noreferrer"
            className={secondaryOnBrandClass}
          >
            <Calendar className="h-5 w-5 shrink-0" aria-hidden />
            日程を選んで面談予約する
          </a>
        </div>
        <p className="mt-6 max-w-prose text-left text-sm leading-relaxed text-[#E4E4E7]">
          外部予約ツールは別サービスです。URLは運用確定後に差し替えてください。
        </p>
      </div>
    </section>
  );
}
