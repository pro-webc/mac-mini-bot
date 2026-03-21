import { Gauge, ShieldCheck, Target } from "lucide-react";

export default function KgsMeasWhatWeMeasureSection() {
  const items = [
    {
      icon: Gauge,
      text: "速度変化・停止・曲線・車線選択など、コース条件に応じた運転操作の傾向（具体アルゴリズムは確定後）",
    },
    {
      icon: Target,
      text: "ヒヤリハットの再現ではなく、訓練・振り返りに資する範囲に限定する方針",
    },
    {
      icon: ShieldCheck,
      text: "測定結果は個人の採点競争にしない進行設計（運営方針として明示）",
    },
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-meas-what-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-meas-what-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          測る対象（概念）
        </h2>
        <ul className="mt-10 space-y-6">
          {items.map(({ icon: Icon, text }) => (
            <li
              key={text}
              className="flex gap-4 border border-[#E4E4E7] bg-[#FFFFFF] p-5"
            >
              <Icon
                className="mt-0.5 h-6 w-6 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <p className="text-left text-base leading-relaxed text-[#18181B]">
                {text}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
