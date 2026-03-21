import { ArrowRight, MessageCircle } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function TrafficApproachCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-approach-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-approach-cta-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          運用に合わせた進行案を一緒に作ります
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          タイムレックス等の日程調整は導線確定後に接続。
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <MessageCircle className="h-5 w-5 shrink-0" aria-hidden />
            <span>実施イメージを相談する</span>
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
