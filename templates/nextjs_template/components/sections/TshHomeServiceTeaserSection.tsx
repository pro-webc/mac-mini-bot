import Link from "next/link";
import { ArrowRight } from "lucide-react";

const cards = [
  {
    title: "サービス概要",
    text: "課題の型、机上講義との違い、データの扱い方針までを整理します。",
    link_label: "サービス概要を見る",
    href: "/service",
  },
  {
    title: "プログラム",
    text: "対象、当日の流れ、事前準備のイメージを具体化します。",
    link_label: "プログラムを見る",
    href: "/program",
  },
  {
    title: "お役立ち情報",
    text: "朝礼で読める短いコラムを掲載します。",
    link_label: "一口アドバイスを読む",
    href: "/tips",
  },
];

export default function TshHomeServiceTeaserSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="service-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="service-teaser-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          提供内容の全体像
        </h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {cards.map((c) => (
            <article
              key={c.href}
              className="flex flex-col justify-between border border-[#e7e5e4] bg-[#fafaf9] p-6"
            >
              <div>
                <h3 className="text-lg font-semibold text-[#1c1917]">
                  {c.title}
                </h3>
                <p className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                  {c.text}
                </p>
              </div>
              <Link
                href={c.href}
                className="mt-6 inline-flex min-h-[44px] items-center gap-2 text-sm font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
              >
                {c.link_label}
                <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
              </Link>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
