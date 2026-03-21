import Link from "next/link";
import { ChevronRight } from "lucide-react";
import type { BlogPost } from "@/lib/blog-posts";

type Props = {
  posts: BlogPost[];
};

export default function HomeBlogTeaserSection({ posts }: Props) {
  const latest = posts.slice(0, 3);
  if (latest.length === 0) return null;

  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="blog-teaser-heading"
    >
      <h2
        id="blog-teaser-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        ブログ（最新記事）
      </h2>
      <p className="mt-3 max-w-2xl text-left text-sm leading-relaxed text-[#BFDBFE]">
        カテゴリ例：現場メモ／安全と手順／設備の基礎知識。検索・信頼の土台づくりとして、順次更新します。
      </p>
      <ul className="mt-6 flex flex-col gap-3">
        {latest.map((p) => (
          <li
            key={p.slug}
            className="rounded-[12px] border border-white/15 bg-[#2563eb] px-4 py-3"
          >
            <p className="text-xs font-semibold text-[#caeb25]">{p.category}</p>
            <Link
              href={`/blog/${p.slug}`}
              className="mt-1 block text-base font-semibold text-white hover:text-[#caeb25] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
            >
              {p.title}
            </Link>
            <p className="mt-1 text-xs text-[#93C5FD]">
              {p.date} · 読了の目安 {p.readMinutes} 分
            </p>
            <p className="mt-2 text-left text-sm text-[#E0E7FF]">{p.excerpt}</p>
          </li>
        ))}
      </ul>
      <div className="mt-6">
        <Link
          href="/blog"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-full border-2 border-[#caeb25] bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#caeb25] transition-colors hover:bg-[#1d4ed8] hover:text-white active:bg-[#1e40af] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          ブログ一覧へ
          <ChevronRight className="h-5 w-5" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
