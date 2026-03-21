import Link from "next/link";
import { ArrowRight } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function TrafficHomeHeroSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] motion-safe:transition-[padding]"
      aria-labelledby="traffic-home-hero-h1"
    >
      <div className="mx-auto flex min-h-[80dvh] max-w-6xl flex-col justify-center px-4 py-16 md:px-6 md:py-24">
        <div className="max-w-3xl">
          <h1
            id="traffic-home-hero-h1"
            className="text-left font-bold leading-[1.2] text-[#18181B]"
            style={{
              fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
            }}
          >
            現場の安全運転を、「話しただけ」で終わらせない。
          </h1>
          <p className="mt-6 max-w-[65ch] text-left text-base font-normal leading-[1.75] text-[#18181B]">
            鹿児島を拠点に、企業の安全運転管理者・運行管理担当向けの交通安全教育・研修。コーチング寄りの進行で習慣を言語化し、GPS等の評価で改善点を観点として可視化します。
          </p>
          <p className="mt-4 max-w-[65ch] text-left text-sm leading-relaxed text-[#52525B]">
            ※効果を保証するものではありません。内容は貴社の運用に合わせて設計します。
          </p>
        </div>
        <div className="mt-10 flex w-full max-w-xl flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <span>無料で相談する</span>
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </CtaButton>
          <Link
            href="/approach"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#E4E4E7] bg-[#F4F4F5] px-6 py-3 text-base font-semibold text-[#18181B] transition-colors hover:border-[#0F766E] hover:bg-[#FFFFFF] hover:text-[#0F766E] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            進行と評価の仕組みを見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
