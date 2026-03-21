import Link from "next/link";
import { BookOpen, ChevronRight } from "lucide-react";

export default function RecruitTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="recruit-blog-teaser-heading"
    >
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div className="flex gap-4">
          <BookOpen className="h-12 w-12 shrink-0 text-[#caeb25]" aria-hidden />
          <div>
            <h2
              id="recruit-blog-teaser-heading"
              className="text-xl font-bold text-white md:text-2xl"
            >
              ブログ（現場日記・安全活動）
            </h2>
            <p className="mt-3 max-w-xl text-left text-base leading-relaxed text-[#E0E7FF]">
              現場の記録や安全の取り組み、資格や募集補足などを発信します。採用検討の参考として、一覧もあわせてご覧ください。
            </p>
          </div>
        </div>
        <div className="shrink-0">
          <Link
            href="/blog"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] bg-[#caeb25] px-6 py-3 text-base font-semibold text-[#0F172A] transition-colors hover:bg-[#b8cf1a] active:bg-[#9fb615] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            ブログ一覧へ
            <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
