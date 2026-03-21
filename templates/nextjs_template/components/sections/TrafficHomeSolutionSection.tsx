import { MessageSquareText, Route, Target } from "lucide-react";

const bullets = [
  "一方的な講話に寄せず、ファシリテーションで安全習慣を言語化し、チーム内で共有できる時間をつくる",
  "一般道路コースの自車走行を前提に、GPS等で運転を評価し、弱点を観点として整理する（見せ方はモックで提示可能）",
  "事前ヒアリングで論点を整理し、当日の進行と振り返りまで一貫した設計にする",
];

const icons = [MessageSquareText, Route, Target];

export default function TrafficHomeSolutionSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-solution-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-solution-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          進め方の核：対話で「自分ごと化」、データで「直す所」を示す
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          一方的な講話に寄せず、ファシリテーションで安全習慣を言語化し共有。現場・事故対応の経験を踏まえ、現実的な論点に落とす。評価はスコアや観点で示し、「何を改善するか」を具体化する方向（効果保証はしない）。
        </p>
        <ul className="mt-10 grid gap-4 md:grid-cols-3">
          {bullets.map((t, i) => {
            const Icon = icons[i] ?? MessageSquareText;
            return (
              <li
                key={t}
                className="flex flex-col gap-3 rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-5"
              >
                <Icon className="h-8 w-8 text-[#0F766E]" aria-hidden />
                <p className="text-left text-base leading-relaxed text-[#18181B]">
                  {t}
                </p>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
