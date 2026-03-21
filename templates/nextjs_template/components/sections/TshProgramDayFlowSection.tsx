import ImagePlaceholder from "@/components/ImagePlaceholder";

const steps = [
  { label: "目的と守るべき安全行動の定義", time: "15分" },
  { label: "具体シナリオの共有ワーク", time: "35分" },
  { label: "走行評価の見方（概念）と本人フィードバック", time: "25分" },
  { label: "翌週からの行動計画", time: "15分" },
];

export default function TshProgramDayFlowSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="day-flow-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="day-flow-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          当日の流れ（例）
        </h2>
        <p className="mt-4 text-sm text-[#57534e]">
          時間配分は人数と会場に応じて変更します。
        </p>
        <div className="mt-10 grid gap-10 lg:grid-cols-2 lg:items-start">
          <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
            <ol className="relative space-y-0">
              {steps.map((s, i) => (
                <li key={s.label} className="flex gap-4 pb-8 last:pb-0">
                  <div className="flex flex-col items-center">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#0f766e] text-sm font-bold text-[#ffffff]">
                      {i + 1}
                    </span>
                    {i < steps.length - 1 ? (
                      <span
                        className="mt-2 w-px grow min-h-[2rem] bg-[#e7e5e4]"
                        aria-hidden
                      />
                    ) : null}
                  </div>
                  <div className="min-w-0 pt-1">
                    <p className="text-base font-semibold text-[#1c1917]">
                      {s.label}
                    </p>
                    <p className="mt-1 text-sm text-[#57534e]">{s.time}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <div>
            <ImagePlaceholder
              aspectClassName="aspect-video"
              description="一般道路の安全な直線区間を抽象化：車内ダッシュボードの一部とナビのルート線がぼんやり見える程度。スピード感や危険演出は避け、落ち着いた配色。"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
