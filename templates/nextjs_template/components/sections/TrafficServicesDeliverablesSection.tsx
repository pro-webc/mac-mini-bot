import { FileText, LineChart } from "lucide-react";

export default function TrafficServicesDeliverablesSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-deliverables-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-deliverables-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          お渡しするもの（イメージ）
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-5">
            <FileText className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <p className="mt-3 text-left text-base leading-relaxed text-[#18181B]">
              当日の進行概要（社内共有用の要約）
            </p>
          </div>
          <div className="rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-5">
            <LineChart className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <p className="mt-3 text-left text-base leading-relaxed text-[#18181B]">
              評価結果の見せ方（観点・改善の論点）※個別内容は参加状況により変化
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
