import Link from "next/link";
import { ArrowRight, BookOpen, Car, Users } from "lucide-react";

export default function TrafficHomeServiceTeaserSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-service-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-service-teaser-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          提供メニュー（概要）
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <Car className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <h3 className="mt-3 text-left text-lg font-semibold leading-[1.45] text-[#18181B]">
              対象
            </h3>
            <p className="mt-2 text-left text-base leading-relaxed text-[#52525B]">
              当面は白ナンバー社用車を複数台運用する企業から開始（戦略は段階拡張）。
            </p>
          </div>
          <div className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <Users className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <h3 className="mt-3 text-left text-lg font-semibold leading-[1.45] text-[#18181B]">
              形式
            </h3>
            <p className="mt-2 text-left text-base leading-relaxed text-[#52525B]">
              集合研修／オンサイト等は要確定のため「要相談」で明示。
            </p>
          </div>
          <div className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <BookOpen className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <h3 className="mt-3 text-left text-lg font-semibold leading-[1.45] text-[#18181B]">
              オンライン
            </h3>
            <p className="mt-2 text-left text-base leading-relaxed text-[#52525B]">
              オンライン要素の可否は案件ごとに調整可能な前提でFAQへ誘導。
            </p>
          </div>
        </div>
        <div className="mt-10">
          <Link
            href="/services"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            研修内容を詳しく見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
