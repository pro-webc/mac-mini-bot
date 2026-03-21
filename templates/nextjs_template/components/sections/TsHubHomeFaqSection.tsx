import CtaButton from "@/components/CtaButton";

const items = [
  {
    q: "オンラインだけでも進められますか？",
    a: "可能な範囲で対応します。ただし対話の深さや、走行に関する見える化の方法は実施形式により異なります。まずは目的と制約（人数・拠点・車両）を伺い、最適な組み合わせをご提案します。",
  },
  {
    q: "対象人数に目安はありますか？",
    a: "社内の運用に合わせて設計します。少人数から部門単位まで、まずは希望の規模感をお知らせください。",
  },
  {
    q: "費用はサイトに載っていますか？",
    a: "内容・時間・形式・移動範囲により変動するため、個別見積りが基本です。相談の段階で、目的に対して無理のない範囲を一緒に整理します。",
  },
  {
    q: "走行データや個人情報の扱いは安全ですか？",
    a: "取得する情報の範囲、保存、第三者提供の有無は、実運用と契約内容に沿って明確化します。サイト上の概要と異なる場合は、必ず事前に書面・説明で整合させます。",
  },
];

export default function TsHubHomeFaqSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          よくあるご質問
        </h2>
        <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
          よくいただくご質問をまとめました。内容は貴社の状況により最適化しますので、不明点はお気軽にご相談ください。
        </p>
        <div className="mt-10 space-y-4">
          {items.map(({ q, a }) => (
            <div
              key={q}
              className="border border-[#E4E4E7] bg-[#FFFFFF] p-5 sm:p-6"
            >
              <h3 className="text-left text-base font-semibold text-[#18181B] md:text-lg">
                {q}
              </h3>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {a}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-10">
          <CtaButton href="/contact">この内容で相談する</CtaButton>
        </div>
      </div>
    </section>
  );
}
