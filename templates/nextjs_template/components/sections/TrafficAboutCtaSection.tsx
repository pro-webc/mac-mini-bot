import { ArrowRight, Mail } from "lucide-react";
import Link from "next/link";

export default function TrafficAboutCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-about-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-about-cta-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          まずはヒアリングから
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          公開情報の不足は相談で補完。
        </p>
        <div className="mt-10">
          <Link
            href="/contact"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            <Mail className="h-5 w-5 shrink-0" aria-hidden />
            問い合わせる
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
