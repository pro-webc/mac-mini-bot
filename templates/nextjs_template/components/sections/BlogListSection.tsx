"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { blogPosts } from "@/lib/blog-posts";

const categories = ["すべて", "現場メモ", "安全と手順", "設備の基礎知識"] as const;

export default function BlogListSection() {
  const [tab, setTab] = useState<(typeof categories)[number]>("すべて");

  const filtered = useMemo(() => {
    if (tab === "すべて") return blogPosts;
    return blogPosts.filter((p) => p.category === tab);
  }, [tab]);

  return (
    <section className="overflow-x-hidden pb-8" aria-labelledby="blog-list-heading">
      <header className="mb-10">
        <h1
          id="blog-list-heading"
          className="text-center text-2xl font-bold text-white md:text-left md:text-4xl"
        >
          ブログ
        </h1>
        <p className="mx-auto mt-4 max-w-3xl text-center text-base leading-relaxed text-[#BFDBFE] md:mx-0 md:text-left">
          現場メモ、安全と手順、設備の基礎知識を中心に、通信インフラ工事の理解補助となる記事を掲載します（デモ）。
        </p>
      </header>

      <div
        className="flex flex-wrap gap-2 border-b border-white/15 pb-4"
        role="tablist"
        aria-label="カテゴリ"
      >
        {categories.map((c) => {
          const selected = tab === c;
          return (
            <button
              key={c}
              type="button"
              role="tab"
              aria-selected={selected}
              className={`min-h-[44px] rounded-[10px] border px-4 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25] ${
                selected
                  ? "border-[#caeb25] bg-[#caeb25] text-[#0F172A] hover:bg-[#b5cf1f] active:bg-[#9fb81a]"
                  : "border-white/25 bg-[#1e40af] text-white hover:bg-[#2563eb] active:bg-[#1d4ed8]"
              }`}
              onClick={() => setTab(c)}
            >
              {c}
            </button>
          );
        })}
      </div>

      {filtered.length === 0 ? (
        <p className="mt-8 text-left text-base text-[#E0E7FF]">
          このカテゴリの記事はまだありません。
        </p>
      ) : (
        <ul className="mt-8 flex flex-col gap-4">
          {filtered.map((p) => (
            <li
              key={p.slug}
              className="rounded-[12px] border border-white/20 bg-[#1d4ed8] p-5 transition-colors hover:border-[#caeb25]/50"
            >
              <p className="text-xs font-semibold text-[#caeb25]">{p.category}</p>
              <Link
                href={`/blog/${p.slug}`}
                className="mt-1 block text-lg font-bold text-white hover:text-[#caeb25] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
              >
                {p.title}
              </Link>
              <p className="mt-1 text-xs text-[#93C5FD]">
                {p.date} · 読了の目安 {p.readMinutes} 分
              </p>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">{p.excerpt}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
