import Link from "next/link";
import { ChevronRight, Calendar } from "lucide-react";

export default function TsTipsArchivePolicySection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="archive-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="archive-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          アーカイブ方針（運用ルール）
        </h2>
        <ul className="mt-8 space-y-4 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
          <li className="flex gap-3 text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            <Calendar className="h-5 w-5 shrink-0 text-[#0F766E]" aria-hidden />
            <span>
              新規は週1回追加（クライアント原稿＋制作側の反映枠）
            </span>
          </li>
          <li className="flex gap-3 text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            <Calendar className="h-5 w-5 shrink-0 text-[#0F766E]" aria-hidden />
            <span>
              過去記事は一覧から辿れる（方針。件数が増えたらタグ検討）
            </span>
          </li>
        </ul>
        <div className="mt-10">
          <Link
            href="/contact"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] hover:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
          >
            相談して運用ルールを決める
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
