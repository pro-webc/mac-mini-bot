import { MessageSquare, Share2 } from "lucide-react";

export default function TrafficApproachFacilitationSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-facilitation-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-facilitation-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          ファシリテーションの考え方
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <MessageSquare className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              安全行動をルール暗記で終わらせず、各自の習慣を言語化。
            </p>
          </div>
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <Share2 className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              共有によりチーム内で「良い打ち手」の共通理解を作る。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
