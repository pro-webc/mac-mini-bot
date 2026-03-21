import { ArrowRight, Calendar } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function TrafficHomeFinalCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-final-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-final-cta-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          まずは状況を伺い、最適な進め方をご提案します
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          同時多発の大型案件表現は避け、相談ベースで調整します。見積・実施条件はお問い合わせ後に個別提示します。
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Calendar className="h-5 w-5 shrink-0" aria-hidden />
            <span>日程を調整する</span>
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
