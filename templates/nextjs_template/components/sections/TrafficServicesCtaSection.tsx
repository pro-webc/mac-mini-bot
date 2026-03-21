import { ArrowRight, Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function TrafficServicesCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-services-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-services-cta-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          内容の細部は、貴社の運用に合わせて調整します
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          事前ヒアリングで最適化。
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            <span>相談内容を送る</span>
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
