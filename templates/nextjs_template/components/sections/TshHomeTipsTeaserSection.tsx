import Link from "next/link";
import { ArrowRight } from "lucide-react";

const items = [
  {
    title: "左折前の「最後の二秒」",
    excerpt:
      "ウインカー後に急に減速しない。後続が予測できる減速配分にする。",
    category: "チェック観点",
    href: "/tips#featured_article",
  },
  {
    title: "雨の日は「見える化」より先に距離",
    excerpt:
      "視界が悪い日ほど、車間だけは守り切る。説教より先にルールを一つに絞る。",
    category: "季節リスク",
    href: "/tips#featured_article",
  },
  {
    title: "朝礼で聞く一文",
    excerpt:
      "昨日、安全にできた運転は何だった？ 具体で答えられると学びが残る。",
    category: "意識づけ",
    href: "/tips#featured_article",
  },
];

export default function TshHomeTipsTeaserSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="tips-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="tips-teaser-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          一口アドバイス（最新）
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          毎週ひとつ、朝礼でそのまま読める短さにしています。
        </p>
        <ul className="mt-10 flex flex-col gap-4">
          {items.map((it) => (
            <li key={it.title}>
              <Link
                href={it.href}
                className="block border border-[#e7e5e4] bg-[#fafaf9] p-5 transition-colors hover:border-[#0f766e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
              >
                <p className="text-xs font-semibold text-[#0f766e]">
                  {it.category}
                </p>
                <p className="mt-2 text-lg font-semibold text-[#1c1917]">
                  {it.title}
                </p>
                <p className="mt-2 text-left text-sm leading-relaxed text-[#57534e]">
                  {it.excerpt}
                </p>
              </Link>
            </li>
          ))}
        </ul>
        <div className="mt-8">
          <Link
            href="/tips"
            className="inline-flex min-h-[44px] items-center gap-2 text-base font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          >
            お役立ち情報へ
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
