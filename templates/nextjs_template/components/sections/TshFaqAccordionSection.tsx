const pairs = [
  {
    q: "オンラインだけでも実施できますか？",
    a: "一部は可能です。ただし走行評価や相互フィードバックの質を優先する場合、対面を組み合わせる提案が中心になります。",
  },
  {
    q: "対象人数に目安はありますか？",
    a: "あります。進行の密度を落とさない人数設計にし、大人数の場合は分割や複数回を検討します。",
  },
  {
    q: "効果は数値で示せますか？",
    a: "事故率や違反件数の変化は、要因が多いため因果を断定しません。行動指標の改善に寄せた振り返りは可能ですが、保証はしません。",
  },
  {
    q: "安全運転管理者講習の代替になりますか？",
    a: "法令で定められた講習の代替をうたうものではありません。位置づけは貴社の教育計画の補完です。",
  },
  {
    q: "個人情報や走行データはどう扱いますか？",
    a: "取得範囲、保管、廃棄、アクセス権限を事前に合意します。サイト上の説明は方針であり、詳細は個別確認が必要です。",
  },
  {
    q: "秘密保持はできますか？",
    a: "可能です。必要に応じて秘密保持の取り決めをご用意します。",
  },
  {
    q: "料金の目安を教えてください。",
    a: "人数、回数、移動範囲、評価の有無により変動します。未確定のため、サイト上では金額を掲載せず、要相談として個別にお見積りします。",
  },
  {
    q: "鹿児島市外でも対応できますか？",
    a: "エリアにより調整が必要です。まずは拠点と実施希望範囲をお知らせください。",
  },
  {
    q: "車両は何台あれば相談に値しますか？",
    a: "厳密な下限は設けませんが、業務車の運用が複雑になるほど、対話と仕組み化の効果が出やすい傾向があります。目安はおおむね20台以上を想定していますが、断定はしません。",
  },
  {
    q: "実施までのリードタイムは？",
    a: "日程調整と社内確認の進み方によります。目安はお問い合わせ時にご案内します。",
  },
  {
    q: "社内説明用の資料はありますか？",
    a: "概要資料の共有は可能です。機密に触れる内容は面談で調整します。",
  },
];

export default function TshFaqAccordionSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="faq-acc-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="faq-acc-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          Q&amp;A
        </h2>
        <div className="mt-10 flex flex-col gap-3">
          {pairs.map((p, i) => (
            <details
              key={p.q}
              className="group border border-[#e7e5e4] bg-[#ffffff] p-4 open:border-[#0f766e]"
            >
              <summary className="cursor-pointer list-none text-left font-semibold text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e] motion-safe:transition-colors [&::-webkit-details-marker]:hidden">
                <span className="flex items-start justify-between gap-3">
                  <span>
                    <span className="text-[#0f766e]">Q{i + 1}. </span>
                    {p.q}
                  </span>
                  <span
                    className="mt-1 shrink-0 text-sm text-[#57534e] group-open:hidden"
                    aria-hidden
                  >
                    ＋
                  </span>
                  <span
                    className="mt-1 hidden shrink-0 text-sm text-[#57534e] group-open:inline"
                    aria-hidden
                  >
                    －
                  </span>
                </span>
              </summary>
              <p className="mt-4 border-t border-[#e7e5e4] pt-4 text-left text-base leading-[1.7] text-[#57534e]">
                {p.a}
              </p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
