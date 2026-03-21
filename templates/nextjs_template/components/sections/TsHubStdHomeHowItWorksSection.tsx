import { ClipboardList, PenLine, Users, MapPin, RefreshCw } from "lucide-react";

const steps = [
  {
    title: "現状把握",
    text: "教育の頻度、事故・ヒヤリの扱い、車両運用の実態を伺う",
    Icon: ClipboardList,
  },
  {
    title: "設計",
    text: "集合研修、ワーク、フォローの回数と尺を提案",
    Icon: PenLine,
  },
  {
    title: "実施",
    text: "コーチング型の進行で、参加者が「言える・できる」状態を作る",
    Icon: Users,
  },
  {
    title: "見える化",
    text: "一般道路コースを想定し、GPSを用いた運転評価を可視化（設計は個別）",
    Icon: MapPin,
  },
  {
    title: "定着",
    text: "振り返りで次の週からの運用ルールを短く決める",
    Icon: RefreshCw,
  },
];

export default function TsHubStdHomeHowItWorksSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="how-it-works-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="how-it-works-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          進め方の全体像
        </h2>
        <p className="mt-4 max-w-prose text-left text-sm text-[#64748B]">
          図解はマークアップで表示しています（画像化しません）。
        </p>
        <ol className="mt-10 flex flex-col gap-4 md:flex-row md:flex-wrap md:gap-0">
          {steps.map((s, i) => (
            <li
              key={s.title}
              className="relative flex flex-1 flex-col border border-[#E2E8F0] bg-[#FAFAF9] p-5 md:min-w-[180px] md:border-l-0 md:first:border-l md:first:rounded-l-none"
            >
              <div className="flex items-start gap-3">
                <span
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[#14B8A6] bg-[#FFFFFF] text-sm font-bold text-[#0F766E]"
                  aria-hidden
                >
                  {i + 1}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <s.Icon className="h-5 w-5 text-[#0F766E]" aria-hidden />
                    <h3 className="text-lg font-semibold text-[#0F172A]">
                      {s.title}
                    </h3>
                  </div>
                  <p className="mt-2 text-left text-sm leading-relaxed text-[#64748B]">
                    {s.text}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
