export default function KgsMeasPageHeaderSection() {
  const items = [
    "一般道コース走行を想定し、GPS等のデータを材料に評価・フィードバックへつなげる",
    "個人の熟練度ではなく、組織的な改善サイクルに載せるための指標設計を重視",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-meas-header-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="kgs-meas-header-h1"
          className="text-left text-3xl font-bold tracking-tight text-[#18181B] md:text-4xl"
        >
          走行を前提に、技能と癖の傾向を見える化する
        </h1>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <span className="font-semibold text-[#1D4ED8]">・</span>
              <span>{t}</span>
            </li>
          ))}
        </ul>
        <div className="mt-8 border border-[#E4E4E7] bg-[#FAFAF9] p-5">
          <p className="text-left text-sm font-semibold text-[#18181B]">
            測定の目的とプライバシー原則（先に共有します）
          </p>
          <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B]">
            測定は支配ではなく、振り返りの材料にします。採点競争にしない進行を原則とし、取得目的・保存期間・共有範囲は事前に合意します。
          </p>
        </div>
      </div>
    </section>
  );
}
