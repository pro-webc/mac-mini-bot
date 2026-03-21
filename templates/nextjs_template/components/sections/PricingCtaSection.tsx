import { ChevronRight, Mail } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function PricingCtaSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#0284C7] bg-[#F0F9FF] p-6 md:p-10"
      aria-labelledby="pricing-cta-heading"
    >
      <h2 id="pricing-cta-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        不明点はお問い合わせへ
      </h2>
      <p className="mt-3 max-w-2xl text-left text-base leading-relaxed text-[#475569]">
        表にない内容や、複数箇所まとめてのご相談もお受けします。写真や図面があると見積精度が上がります。
      </p>
      <div className="mt-6">
        <CtaButton href="/contact">
          <span className="inline-flex items-center gap-2">
            <Mail className="h-5 w-5" aria-hidden />
            お問い合わせ
            <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
          </span>
        </CtaButton>
      </div>
    </section>
  );
}
