import { PenLine } from "lucide-react";

export default function TrafficTipsEditorialSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-editorial-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <PenLine className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <div className="min-w-0 flex-1">
            <h2
              id="traffic-editorial-heading"
              className="text-left font-semibold leading-[1.35] text-[#18181B]"
              style={{
                fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
                fontWeight: 650,
              }}
            >
              更新・修正の運用
            </h2>
            <ul className="mt-6 space-y-3 text-left text-base leading-relaxed text-[#18181B]">
              <li className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-4">
                週次更新のたたき台を作り、運用開始後に文言を磨く。
              </li>
              <li className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-4">
                緊急の法令・通達対応は別契約の可能性に言及（断定せず）。
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
