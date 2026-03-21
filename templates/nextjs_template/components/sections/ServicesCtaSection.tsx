import { ChevronRight, Mail } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function ServicesCtaSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#caeb25]/40 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="services-cta-heading"
    >
      <h2
        id="services-cta-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        見積・相談はお問い合わせへ
      </h2>
      <p className="mt-3 max-w-2xl text-left text-base leading-relaxed text-[#BFDBFE]">
        設備種別・現場条件を伺い、対応可否と進め方のたたき台をご返信します。まずはお問い合わせフォームからお送りください。
      </p>
      <div className="mt-6">
        <CtaButton href="/contact">
          <span className="inline-flex items-center gap-2">
            <Mail className="h-5 w-5" aria-hidden />
            お問い合わせフォームへ
            <ChevronRight className="h-5 w-5" aria-hidden />
          </span>
        </CtaButton>
      </div>
    </section>
  );
}
