import Link from "next/link";
import { ChevronRight } from "lucide-react";
import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function HomeWorksTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="works-teaser-heading"
    >
      <h2
        id="works-teaser-heading"
        className="text-center text-xl font-bold text-white md:text-left md:text-2xl"
      >
        実績・事例（公開準備中）
      </h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-base leading-relaxed text-[#BFDBFE] md:mx-0 md:text-left">
        掲載基準と転記範囲が確定次第、写真と概要を追加します。参考イメージはグループ関連サイトの構成を踏まえつつ、本文企業向けに再構成します。
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <ImagePlaceholder
          aspectClassName="aspect-video"
          description="掲載予定：屋外基地局またはレーン設備の施工前後が分かるカット。モザイク方針は法務確認後に確定。"
          overlayText="事例ビジュアル枠（Before想定）"
        />
        <ImagePlaceholder
          aspectClassName="aspect-video"
          description="掲載予定：配線・ラック周りの整った仕上がり。ロゴ・個人情報の映り込みに注意した構図。"
          overlayText="事例ビジュアル枠（After想定）"
        />
      </div>
      <div className="mt-8 flex justify-center md:justify-start">
        <Link
          href="/works"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] bg-[#caeb25] px-6 py-3 text-base font-semibold text-[#0F172A] transition-colors hover:bg-[#b8cf1a] active:bg-[#9fb615] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          実績・事例ページへ
          <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
