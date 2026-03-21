const faqs = [
  {
    q: "未経験でも応募は可能ですか？",
    a: "可能性はあります。まずはフォームから経歴と希望をお送りください。現場配属にあたっての前提条件は、選考のなかで個別にご説明します。",
  },
  {
    q: "勤務地や出張について教えてください。",
    a: "拠点は大阪周辺を想定しつつ、案件によっては出張・宿泊が発生し得ます。頻度や条件は、募集ポジションと時期によって異なるため、お問い合わせください。",
  },
  {
    q: "資格は必須ですか？",
    a: "工事内容により必要な資格・技能が変わります。保有資格がない場合でも、配属先や研修の方針により対応が変わるため、まずはご相談ください。",
  },
  {
    q: "夜勤や休日対応はありますか？",
    a: "案件によります。希望や制約がある方は、応募・相談段階でお知らせください。",
  },
  {
    q: "協力会社としての連携は可能ですか？",
    a: "可能です。協業希望の方はお問い合わせフォームの区分で「協業・協力会社」を選択し、可能な範囲で体制・エリア・工程を記載ください。",
  },
  {
    q: "服装や保護具はどうなりますか？",
    a: "現場ルールと案件の前提に合わせて指定します。詳細は選考・配属前の説明で共有します。不明点はお問い合わせください。",
  },
  {
    q: "選考期間の目安はありますか？",
    a: "応募状況や確認事項により変動します。急ぎの場合はフォームに記載いただくか、お電話でもお知らせください。詳細はお問い合わせください。",
  },
];

export default function RecruitFaqSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#E2E8F0] bg-white p-6 md:p-10"
      aria-labelledby="recruit-faq-heading"
    >
      <h2
        id="recruit-faq-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        よくある質問
      </h2>
      <p className="mt-3 text-left text-sm text-[#475569]">
        個別の条件は案件・時期により異なります。末尾の項目についても、詳細はお問い合わせください。
      </p>
      <ul className="mt-8 space-y-4">
        {faqs.map((f) => (
          <li
            key={f.q}
            className="rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-5"
          >
            <p className="text-base font-semibold text-[#0F172A]">{f.q}</p>
            <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">{f.a}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
