import Link from "next/link";
import { Sparkles, ChevronRight } from "lucide-react";

export default function HomeRecruitTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="home-recruit-teaser-heading"
    >
      <h2
        id="home-recruit-teaser-heading"
        className="inline-flex items-center gap-2 text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        <Sparkles className="h-7 w-7 text-[#2563eb]" aria-hidden />
        採用のひとこと
      </h2>
      <p className="mt-3 max-w-2xl text-left text-base leading-relaxed text-[#475569]">
        かっこいい装備と手に職。稼ぎがいい土台を、チームでつくる——古い現場イメージを更新する「新しい3K」へ。未経験・経験者ともに、まずは募集概要とブログで雰囲気を覗いてみてください。
      </p>
      <div className="mt-6 flex justify-start">
        <Link
          href="/recruit"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] bg-[#2563eb] px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-[#1d4ed8] active:bg-[#1e40af] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          採用情報を見る
          <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
