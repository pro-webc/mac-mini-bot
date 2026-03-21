import { Database } from "lucide-react";

export default function TrafficApproachDataPrivacySection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-data-privacy-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Database className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <div className="min-w-0 flex-1">
            <h2
              id="traffic-data-privacy-heading"
              className="text-left font-semibold leading-[1.35] text-[#18181B]"
              style={{
                fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
                fontWeight: 650,
              }}
            >
              データの取り扱い（方針レベル）
            </h2>
            <ul className="mt-6 space-y-3 text-left text-base leading-relaxed text-[#18181B]">
              <li className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-4">
                目的限定・保管期間・第三者提供の有無は確定次第で明記。
              </li>
              <li className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-4">
                現時点は「お問い合わせ時にご説明」で運用。
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
