import Link from "next/link";
import { CircleDollarSign, ChevronRight } from "lucide-react";

export default function HomePricingTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="pricing-teaser-heading"
    >
      <h2
        id="pricing-teaser-heading"
        className="inline-flex items-center gap-2 text-center text-xl font-bold text-[#0F172A] md:text-left md:text-2xl"
      >
        <CircleDollarSign className="h-7 w-7 text-[#0284C7]" aria-hidden />
        料金の目安
      </h2>
      <p className="mt-3 text-left text-base leading-relaxed text-[#475569]">
        現地の状況や部材の種類により金額が変動します。サイト上では代表例を表形式で掲載し、最終的な金額はお見積りにてご提示します。
      </p>
      <div className="mt-6 rounded-none border border-[#E2E8F0] bg-[#F8FAFC] p-4">
        <p className="text-sm font-semibold text-[#0F172A]">いま表示できる例（仮）</p>
        <ul className="mt-2 list-inside list-disc text-sm leading-relaxed text-[#475569]">
          <li>出張・現地調査：◯◯円〜（税込／確定値は別途）</li>
          <li>標準的な交換作業：◯◯円〜（税込／確定値は別途）</li>
        </ul>
      </div>
      <div className="mt-6 flex justify-center md:justify-start">
        <Link
          href="/pricing"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] bg-[#0284C7] px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-[#0369A1] active:bg-[#075985] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
        >
          料金ページで詳しく見る
          <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
