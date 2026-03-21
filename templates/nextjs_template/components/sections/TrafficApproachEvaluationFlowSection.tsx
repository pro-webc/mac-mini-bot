import { Car, ClipboardList, ShieldCheck } from "lucide-react";

const phases = [
  {
    phase: "事前",
    body: "コース概要、注意事項、データ取り扱いの説明",
    Icon: ClipboardList,
  },
  {
    phase: "当日",
    body: "走行→データ確認→観点フィードバック（デモは匿名化モック）",
    Icon: Car,
  },
  {
    phase: "事後",
    body: "改善の論点を文書化しやすい形で整理",
    Icon: ShieldCheck,
  },
];

export default function TrafficApproachEvaluationFlowSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-eval-flow-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-eval-flow-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          自車走行評価の流れ（概念）
        </h2>
        <div className="mt-8 overflow-x-auto">
          <div className="flex min-w-[min(100%,720px)] flex-col gap-4 md:flex-row md:items-stretch md:gap-0">
            {phases.map(({ phase, body, Icon }, i) => (
              <div
                key={phase}
                className="flex flex-1 flex-col border border-[#E4E4E7] bg-[#FAFAF9] p-5 md:border-l-0 md:first:border-l md:first:rounded-l-sm md:last:rounded-r-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="flex h-9 w-9 items-center justify-center rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] text-sm font-bold text-[#0F766E]">
                    {i + 1}
                  </span>
                  <Icon className="h-6 w-6 text-[#0F766E]" aria-hidden />
                  <span className="text-sm font-semibold text-[#0F766E]">
                    {phase}
                  </span>
                </div>
                <p className="mt-4 text-left text-base leading-relaxed text-[#18181B]">
                  {body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
