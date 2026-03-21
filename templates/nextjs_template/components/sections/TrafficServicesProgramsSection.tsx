import { ClipboardList, Mic, Navigation, Users } from "lucide-react";

const programs: { text: string; Icon: typeof Users }[] = [
  {
    text: "安全習慣の言語化・共有ワーク（コーチング寄りファシリテーション）",
    Icon: Users,
  },
  {
    text: "管理者向け：朝礼で使える短いフレーム（観点・問いかけ）の提供イメージ",
    Icon: Mic,
  },
  {
    text: "自車走行評価：一般道路コースでの走行を前提に、GPS等で観点整理（レポートはモックで提示）",
    Icon: Navigation,
  },
];

export default function TrafficServicesProgramsSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-programs-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <ClipboardList className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <h2
            id="traffic-programs-heading"
            className="text-left font-semibold leading-[1.35] text-[#18181B]"
            style={{
              fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
              fontWeight: 650,
            }}
          >
            主なプログラム構成（例）
          </h2>
        </div>
        <ul className="mt-10 grid gap-4 md:grid-cols-3">
          {programs.map(({ text, Icon }) => (
            <li
              key={text}
              className="flex flex-col gap-3 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5"
            >
              <Icon className="h-8 w-8 text-[#0F766E]" aria-hidden />
              <p className="text-left text-base leading-relaxed text-[#18181B]">
                {text}
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-6 max-w-[65ch] text-left text-sm leading-relaxed text-[#52525B]">
          ※時間・回数・集合形式はヒアリング確定後に表記を固定。
        </p>
      </div>
    </section>
  );
}
