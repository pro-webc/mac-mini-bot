const items = [
  {
    q: "見積もりに必要な情報は？",
    a: "設置場所の概要、設備種別、希望日程、既存資料（図面・写真）があれば共有ください。ない場合はヒアリングから開始します。",
  },
  {
    q: "対応エリアは？",
    a: "全国対応を想定しています。遠方の場合はオンライン打合せと現地作業の回数設計をご提案します。",
  },
  {
    q: "工期が厳しい案件でも相談できますか？",
    a: "可能な限り調整しますが、安全確保と法令順守を最優先します。制約が出る場合は早めに代替案を共有します。",
  },
  {
    q: "夜間・休日の作業は？",
    a: "現場ルール・許可・協力体制により異なります。要件を伺い、可否と手順を整理します。",
  },
  {
    q: "保守の範囲は？",
    a: "契約条件によります。定期点検、障害時対応、部品手配の切り分けなど、事前に合意形成します。",
  },
  {
    q: "協力会社としての連携は？",
    a: "可能です。持ち場・工程・安全管理のすり合わせから入ります。",
  },
];

export default function FaqServicesSection() {
  return (
    <section className="bg-[#FFFFFF] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          よくあるご質問
        </h2>
        <p className="mt-4 text-left text-sm font-medium text-[#0F172A]">
          数値実績や可否の断定は案件ごとに異なります。不明点はお問い合わせください。
        </p>
        <ul className="mt-8 space-y-4">
          {items.map((item) => (
            <li
              key={item.q}
              className="rounded-[16px] border border-[#E2E8F0] bg-[#F8FAFC] p-5"
            >
              <p className="text-base font-semibold text-[#0F172A]">{item.q}</p>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">{item.a}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
