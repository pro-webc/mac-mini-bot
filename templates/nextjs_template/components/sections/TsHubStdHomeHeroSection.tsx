import ImagePlaceholder from "@/components/ImagePlaceholder";
import CtaButton from "@/components/CtaButton";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function TsHubStdHomeHeroSection() {
  return (
    <section
      className="flex min-h-[80vh] flex-col justify-center border-b border-[#E2E8F0] bg-[#FFFFFF] pb-16 pt-8 md:pb-20"
      aria-labelledby="home-hero-heading"
    >
      <div className="mx-auto grid max-w-6xl gap-10 px-4 md:grid-cols-2 md:items-center md:px-6">
        <div className="order-2 md:order-1">
          <p className="text-sm font-medium tracking-wide text-[#0F766E]">
            鹿児島市周辺の法人向け
          </p>
          <h1
            id="home-hero-heading"
            className="mt-3 text-3xl font-bold leading-tight tracking-tight text-[#0F172A] md:text-4xl"
          >
            社用車の安全運転を、講義だけで終わらせない。
          </h1>
          <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
            安全運転管理者・運行管理者の方へ。コーチング型の対話で「再現できる行動」に落とし込み、GPSを用いた運転評価の見える化で改善の材料をそろえます。
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
            <CtaButton href="/contact">無料相談する</CtaButton>
            <Link
              href="/services"
              className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:border-[#115e59] hover:bg-[#F0FDFA] hover:text-[#115e59] active:bg-[#CCFBF1] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6] motion-safe:transition-colors"
            >
              <span>サービスを見る</span>
              <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            </Link>
          </div>
          <p className="mt-6 text-sm text-[#64748B]">
            対応エリア・実施形式は、初回ヒアリングで確認します。
          </p>
        </div>
        <div className="order-1 md:order-2">
          <ImagePlaceholder
            aspectClassName="aspect-video"
            description="ヒーロー主視覚：鹿児島の朝の街路を柔らかい自然光で。車は一般車の後方イメージに留め、特定ナンバーや看板文字は識別できないボケ。人物は威圧感のない運転手の横顔シルエット程度。全体トーンはティールアクセントと相性の良いニュートラル。"
            overlayText="社用車の安全を、現場の習慣まで。"
          />
        </div>
      </div>
    </section>
  );
}
