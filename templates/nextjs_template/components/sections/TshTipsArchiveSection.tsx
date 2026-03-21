import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function TshTipsArchiveSection() {
  return (
    <section
      id="archive_hint"
      className="scroll-mt-[calc(10vh+1rem)] border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="archive-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="archive-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          過去記事へ
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          同じカテゴリの記事は、新着一覧から辿れます。運用に合わせて記事を追加していきます。
        </p>
        <div className="mt-8">
          <Link
            href="/tips#tips-list-heading"
            className="inline-flex min-h-[44px] items-center gap-2 text-base font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          >
            一覧の先頭へ戻る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
