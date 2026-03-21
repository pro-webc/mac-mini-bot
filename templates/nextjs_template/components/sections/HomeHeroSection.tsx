import Link from "next/link";
import { Cable, ChevronRight } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function HomeHeroSection() {
  return (
    <section
      className="mt-[10vh] flex min-h-[80svh] flex-col gap-8 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1e40af] p-6 md:flex-row md:items-center md:gap-10 md:p-10"
      aria-labelledby="hero-heading"
    >
      <div className="flex flex-1 flex-col justify-center gap-6">
        <p className="inline-flex w-fit items-center gap-2 rounded-[8px] border border-[#caeb25]/40 bg-[#2563eb] px-3 py-1 text-xs font-semibold text-[#caeb25]">
          <Cable className="h-4 w-4 text-[#caeb25]" aria-hidden />
          インフラを、現場からつなぐ。
        </p>
        <h1
          id="hero-heading"
          className="text-center text-2xl font-bold leading-tight text-white sm:text-3xl md:text-left md:text-4xl"
        >
          つくるのは設備だけじゃない。現場と、次の標準を。
        </h1>
        <p className="text-center text-base leading-relaxed text-[#BFDBFE] md:text-left md:text-lg">
          株式会社ワン・ピースは、携帯電話基地局やETCレーンなど、生活インフラに直結する通信設備の工事に携わります。オンラインでの打合せと現場作業を組み合わせ、遠方案件でも進めやすいコミュニケーションを心がけています。
        </p>
        <p className="text-center text-sm leading-relaxed text-[#93C5FD] md:text-left">
          LINE公式はURL確定後にご案内内ボタンを設置します。
        </p>
        <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-start">
          <CtaButton href="/contact">
            <span className="inline-flex items-center gap-2">
              お問い合わせする
              <ChevronRight className="h-5 w-5" aria-hidden />
            </span>
          </CtaButton>
          <Link
            href="/services"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-full border-2 border-[#caeb25] bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#caeb25] transition-colors hover:border-white hover:bg-[#1d4ed8] hover:text-white active:border-[#BFDBFE] active:bg-[#1e3a8a] active:text-[#E0E7FF] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            サービスを見る
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </div>
      <div className="w-full flex-1">
        <ImagePlaceholder
          aspectClassName="aspect-[4/3]"
          description="掲載予定：夜の基地局マスト風のシルエット、高所作業の安全装備イメージ。クールで勢いのあるコーポレートトーン。実素材は許諾確定後に public/images/generated/ へ差し替え。"
          overlayText="夜の基地局・高所作業シルエット（撮影・差し替え想定）"
        />
      </div>
    </section>
  );
}
