export default function KgsHomeValuePropSection() {
  const items = [
    "ワークとファシリテーションで、参加者が安全行動や工夫を言語化し、他者事例から学ぶ場をつくる",
    "一般道コース走行を想定し、GPS等のデータを材料にスコア化・弱点の可視化・フィードバックへつなげる（詳細仕様はヒアリングで確定）",
    "導入は無理のない範囲から：事前ヒアリング→提案→実施→振り返りの型を明示",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-home-value-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-value-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          提供の中心：対話で「自分ごと」にし、測れる形に近づける
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#1D4ED8]" aria-hidden />
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
