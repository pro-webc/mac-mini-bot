import { ClipboardList, Users, Target } from "lucide-react";

const steps = [
  {
    title: "目的と論点のすり合わせ",
    text: "貴社の車両運用、教育方針、いま困っている点を短時間で整理します。",
    Icon: ClipboardList,
  },
  {
    title: "体験と気づきの共有",
    text: "ワークと対話を組み合わせ、現場の当事者が「言える化」できるように進めます。",
    Icon: Users,
  },
  {
    title: "優先課題と次の一歩",
    text: "大きなスローガンではなく、翌週から試せる行動に落とします。",
    Icon: Target,
  },
];

export default function TsHubHomeHowItWorksSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          当日の進行イメージ（例）
        </h2>
        <ol className="mt-10 grid gap-6 md:grid-cols-3">
          {steps.map(({ title, text, Icon }, i) => (
            <li
              key={title}
              className="relative border border-[#E4E4E7] bg-[#FAFAF9] p-5 sm:p-6"
            >
              <div className="flex items-start gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 border-[#1D4ED8] text-sm font-bold text-[#1D4ED8]">
                  {i + 1}
                </span>
                <Icon className="mt-2 h-6 w-6 text-[#1D4ED8]" aria-hidden />
              </div>
              <h3 className="mt-4 text-left text-lg font-semibold text-[#18181B]">
                {title}
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {text}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
