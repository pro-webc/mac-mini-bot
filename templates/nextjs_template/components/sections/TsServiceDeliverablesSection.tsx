import { CircleArrowRight, FileText, ListChecks } from "lucide-react";

export default function TsServiceDeliverablesSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="deliverables-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="deliverables-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          当日・直後に残るもの
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <FileText className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              進行の要点整理（社内共有用の言い回し例）
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <ListChecks className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              改善の観点リスト（現場で使えるチェックの考え方）
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <CircleArrowRight className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              次のアクション提案（小さく始める運用）
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
