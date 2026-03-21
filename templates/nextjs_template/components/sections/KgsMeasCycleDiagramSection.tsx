const steps = [
  { key: "Plan", title: "Plan", body: "目的と評価観点の合意" },
  { key: "Do", title: "Do", body: "講習と走行セッション" },
  { key: "Check", title: "Check", body: "可視化レポートとチーム対話" },
  { key: "Act", title: "Act", body: "現場ルール・点呼・教育ネタへの反映" },
];

export default function KgsMeasCycleDiagramSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-meas-cycle-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-meas-cycle-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          PDCAの置き方（図解はマークアップで）
        </h2>
        <div className="mt-10 overflow-x-auto">
          <div className="flex min-w-[640px] items-stretch justify-between gap-3 md:min-w-0">
            {steps.map((s, i) => (
              <div key={s.key} className="flex flex-1 items-center gap-2">
                <article className="flex min-h-[140px] flex-1 flex-col border-2 border-[#1D4ED8] bg-[#FAFAF9] p-4">
                  <h3 className="text-left text-lg font-bold text-[#1D4ED8]">
                    {s.title}
                  </h3>
                  <p className="mt-2 text-left text-sm leading-relaxed text-[#18181B]">
                    {s.body}
                  </p>
                </article>
                {i < steps.length - 1 ? (
                  <span
                    className="hidden shrink-0 text-2xl font-bold text-[#52525B] md:inline"
                    aria-hidden
                  >
                    →
                  </span>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
