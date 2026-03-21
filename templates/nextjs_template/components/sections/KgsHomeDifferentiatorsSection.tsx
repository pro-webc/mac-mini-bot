export default function KgsHomeDifferentiatorsSection() {
  const items = [
    "交通安全関連の長年の実務経験（現場・事故対応の文脈）に基づく設計思想※数値の断定はしない",
    "白ナンバー運用が多い企業の安全管理部門に刺さる導線を優先し、運輸系事業者への展開は段階的に",
    "一人運営のため同時多発の大型案件は想定しない旨を正直に示し、期待値を適正化",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-home-diff-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-diff-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          なぜこの支援が現場に刺さりやすいか
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="border border-[#E4E4E7] bg-[#FFFFFF] p-4">
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
