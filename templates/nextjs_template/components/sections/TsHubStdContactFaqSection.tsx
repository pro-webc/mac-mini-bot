const items = [
  {
    q: "オンラインだけで完結しますか？",
    a: "初回の打ち合わせやフォローはオンライン対応が可能です。実車を伴う内容が適切な場合は、安全と法令遵守を優先して計画し、事前にご説明します。",
  },
  {
    q: "教育内容は会社ごとに変わりますか？",
    a: "変わります。車両台数、運行形態、既存の社内ルール、対象者の職種に合わせて設計します。",
  },
  {
    q: "GPSの見える化は必須ですか？",
    a: "必須ではありません。課題と目的に応じて、講習・ワーク中心の提案も可能です。導入する場合は、説明範囲とプライバシー配慮を事前に共有します。",
  },
  {
    q: "費用はどのくらいかかりますか？",
    a: "内容、回数、人数、移動範囲によって異なります。フォームに概要を送っていただければ、初回返信で大まかな進め方と確認事項をご案内します。",
  },
];

export default function TsHubStdContactFaqSection() {
  return (
    <section className="bg-[#FAFAF9] py-16 md:py-20" aria-labelledby="faq-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="faq-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          よくあるご質問
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#64748B]">
          よくいただくご質問をまとめました。個別の条件によって答えが変わる内容は、初回ヒアリングで具体化します。
        </p>
        <ul className="mt-10 flex flex-col gap-6">
          {items.map((item) => (
            <li
              key={item.q}
              className="rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6"
            >
              <h3 className="text-lg font-semibold text-[#0F172A]">{item.q}</h3>
              <p className="mt-3 text-left text-base leading-[1.7] text-[#64748B]">
                {item.a}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
