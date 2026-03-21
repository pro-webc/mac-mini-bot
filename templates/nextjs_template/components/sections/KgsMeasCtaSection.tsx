import { Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function KgsMeasCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-24"
      aria-labelledby="kgs-meas-cta-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-meas-cta-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          評価仕様を自社条件に合わせて詰めたい
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-relaxed text-[#18181B]">
          車載機器の有無、走行コース候補、個人情報規程の要望を伺います
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            仕様相談の依頼を送る
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
