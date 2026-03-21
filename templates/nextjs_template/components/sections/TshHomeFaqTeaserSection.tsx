import Link from "next/link";
import { ArrowRight } from "lucide-react";

const items = [
  {
    q: "オンラインだけでも可能ですか？",
    a: "一部は可能ですが、目的に応じて対面・走行を組み合わせる提案が中心です。",
  },
  {
    q: "効果はどれくらいで出ますか？",
    a: "組織の運用設計に依存します。数値保証は行いません。",
  },
  {
    q: "人数に制限はありますか？",
    a: "目安を伺い、進行品質が落ちない人数設計をします。",
  },
];

export default function TshHomeFaqTeaserSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="faq-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="faq-teaser-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          よくあるご質問
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          事前に多い質問をまとめました。
        </p>
        <div className="mt-10 flex flex-col gap-4">
          {items.map((it) => (
            <article
              key={it.q}
              className="border border-[#e7e5e4] bg-[#ffffff] p-5"
            >
              <h3 className="text-base font-semibold text-[#1c1917]">{it.q}</h3>
              <p className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                {it.a}
              </p>
            </article>
          ))}
        </div>
        <div className="mt-8">
          <Link
            href="/faq"
            className="inline-flex min-h-[44px] items-center gap-2 text-base font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          >
            FAQをすべて見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
