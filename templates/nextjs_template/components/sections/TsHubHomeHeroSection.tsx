import ImagePlaceholder from "@/components/ImagePlaceholder";
import CtaButton from "@/components/CtaButton";
import Link from "next/link";

export default function TsHubHomeHeroSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] pb-16 pt-6 md:pb-20 md:pt-8"
      aria-labelledby="home-hero-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-12">
          <div>
            <p className="text-left text-sm font-semibold tracking-tight text-[#1D4ED8]">
              鹿児島｜企業向け
            </p>
            <h1
              id="home-hero-heading"
              className="mt-3 text-left text-3xl font-bold leading-tight tracking-tight text-[#18181B] md:text-4xl lg:text-[2.75rem]"
            >
              現場が「自分ごと」になる、交通安全の伴走支援。
            </h1>
            <p className="mt-5 max-w-prose text-left text-base leading-[1.75] text-[#52525B] md:text-lg">
              安全運転管理者・運行管理担当者向けに、コーチング型の研修と、一般道路コースを前提とした運転の見える化（GPS等）で、改善の優先順位を一緒に整理します。押しつけではなく、腹落ちから始めます。
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
              <CtaButton href="/contact">無料で相談する</CtaButton>
              <Link
                href="/services"
                className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center rounded-[12px] border-2 border-[#1D4ED8] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:bg-[#EFF6FF] active:bg-[#DBEAFE] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
              >
                サービスを見る
              </Link>
            </div>
          </div>
          <div>
            <ImagePlaceholder
              description="柔らかい自然光のオフィスまたは明るい研修室。参加者がホワイトボード前で付箋を並べている様子。交通安全の原色や警告色は避け、ネイビー・グレー・白の服装。親しみやすく落ち着いた雰囲気。"
              aspectClassName="aspect-video"
              overlayText="伴走型の対話と、現場に残る言葉づくり"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
