import { MessageCircle } from "lucide-react";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import CtaButton from "@/components/CtaButton";

export default function TsHubHeroSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="hero-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="relative overflow-hidden rounded-none border border-[#E4E4E7] bg-[#FAFAF9]">
          <ImagePlaceholder
            description="交通安全の硬さを和らげる柔らかいタッチのヒーロー用ビジュアル（写真またはイラスト）。後工程で差し替え。"
            aspectClassName="aspect-[16/10] min-h-[280px] md:min-h-[360px]"
          />
          <div className="pointer-events-none absolute inset-0 z-[5] flex flex-col justify-end bg-gradient-to-t from-[#18181B]/75 via-[#18181B]/25 to-transparent p-6 md:p-10 md:from-[#18181B]/60" />
          <div className="absolute inset-x-0 bottom-0 z-20 p-6 md:p-10">
            <h1
              id="hero-heading"
              className="text-left text-2xl font-bold leading-tight tracking-tight text-[#FFFFFF] md:text-4xl"
            >
              日常の運転と管理を、見える化して改善する
            </h1>
          </div>
        </div>
        <div className="mt-8 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>
            鹿児島市周辺の企業向けに、交通安全教育・講習を提供します。説教に寄らない対話と、見える化・評価で、担当者の説明負荷を下げながら現場の意識づくりを支援します。
          </p>
          <p className="text-sm text-[#52525B]">
            全国への大量集客は目的としません。地域の担当者に、誤解なく価値が伝わる説明を優先します。
          </p>
        </div>
        <ul className="mt-8 space-y-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
          <li className="flex gap-3 text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            <MessageCircle
              className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]"
              aria-hidden
            />
            <span>
              鹿児島市周辺の企業向け：交通安全教育・講習
            </span>
          </li>
          <li className="flex gap-3 text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            <MessageCircle
              className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]"
              aria-hidden
            />
            <span>
              安全運転管理者・運行管理者など、担当者の負担を下げる進め方
            </span>
          </li>
          <li className="flex gap-3 text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            <MessageCircle
              className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]"
              aria-hidden
            />
            <span>
              説教ではなく、対話と共有で「自分ごと化」する設計
            </span>
          </li>
        </ul>
        <div className="mt-8 flex flex-wrap gap-4">
          <CtaButton href="/contact">
            <MessageCircle className="h-5 w-5" aria-hidden />
            無料で相談する
          </CtaButton>
        </div>
        <p className="mt-6 text-left text-sm text-[#52525B]">
          週1回の短いアドバイスを掲載予定です。対象は鹿児島市周辺で社用車・営業車を運用する企業の管理・総務・現場リーダー層を想定しています。
        </p>
      </div>
    </section>
  );
}
