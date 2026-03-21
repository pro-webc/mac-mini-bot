const steps = [
  { n: "1", label: "応募", sub: "フォームまたはお電話で希望・経歴をお送りください。" },
  { n: "2", label: "面談", sub: "現場イメージと前提条件をすり合わせます。" },
  { n: "3", label: "条件調整", sub: "配属・勤務条件など、個別にご説明します。" },
  { n: "4", label: "配属イメージ", sub: "チーム編成と業務範囲のたたき台を共有します（抽象）。" },
];

export default function RecruitFlowSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="recruit-flow-heading"
    >
      <h2
        id="recruit-flow-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        応募から配属イメージまで（概要）
      </h2>
      <p className="mt-3 max-w-3xl text-left text-sm leading-relaxed text-[#BFDBFE]">
        実際の選考ステップは時期により更新します。以下は理解しやすさのための抽象フローです。
      </p>
      <div className="mt-8 overflow-x-auto">
        <ol className="flex min-w-[600px] list-none gap-3 md:min-w-0">
          {steps.map((s) => (
            <li
              key={s.n}
              className="flex flex-1 flex-col rounded-[12px] border border-white/20 bg-[#2563eb] p-4"
            >
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#caeb25] text-sm font-bold text-[#0F172A]">
                {s.n}
              </span>
              <p className="mt-3 text-base font-semibold text-white">{s.label}</p>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">{s.sub}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
