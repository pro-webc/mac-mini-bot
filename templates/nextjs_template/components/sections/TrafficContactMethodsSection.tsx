import { CalendarClock, Phone } from "lucide-react";

export default function TrafficContactMethodsSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-contact-methods-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-contact-methods-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          相談の進め方
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <CalendarClock className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              フォーム送信後、日程調整用リンクを返信で案内（アカウント方針は確定待ち）。
            </p>
          </div>
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <Phone className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              電話番号は確定次第ヘッダー・フッターに表示。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
