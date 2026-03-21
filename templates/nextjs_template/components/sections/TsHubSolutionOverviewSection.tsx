import Link from "next/link";
import { ChevronRight, Eye, MessageSquare, Route } from "lucide-react";

const blocks = [
  {
    title: "対話",
    body: "各自の安全意識の立ち上がり方を言語化し、チームで共有する",
    Icon: MessageSquare,
  },
  {
    title: "可視化",
    body: "機材を用いて状態を見える化し、本人の気づきから改善につなげる",
    Icon: Eye,
  },
  {
    title: "評価",
    body: "一般道路コースを自社車両で走行し、GPS等に基づきスコア化。減点理由を説明し「事故前に直せる」感覚をつくる",
    Icon: Route,
  },
];

export default function TsHubSolutionOverviewSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="solution-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="solution-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          進め方の全体像（対話・可視化・評価）
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.75] text-[#18181B]">
          対話・可視化・評価の三つを組み合わせ、一方通行の説教に留まらない改善の流れをつくります。
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {blocks.map(({ title, body, Icon }, i) => (
            <div
              key={title}
              className="relative flex flex-col gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-5"
            >
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-full border border-[#E4E4E7] text-xs font-semibold text-[#0F766E]">
                  {i + 1}
                </span>
                <Icon className="h-6 w-6 text-[#0F766E]" aria-hidden />
                <h3 className="text-base font-semibold text-[#18181B]">
                  {title}
                </h3>
              </div>
              <p className="text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {body}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-8 hidden md:block">
          <div className="flex flex-wrap items-center justify-center gap-2 text-sm font-medium text-[#52525B]">
            <span className="rounded border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2">
              対話
            </span>
            <ChevronRight className="h-4 w-4 text-[#0F766E]" aria-hidden />
            <span className="rounded border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2">
              可視化
            </span>
            <ChevronRight className="h-4 w-4 text-[#0F766E]" aria-hidden />
            <span className="rounded border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2">
              評価
            </span>
            <ChevronRight className="h-4 w-4 text-[#0F766E]" aria-hidden />
            <span className="rounded border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2">
              改善の共有
            </span>
          </div>
        </div>
        <div className="mt-10">
          <Link
            href="/approach"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#FAFAF9] active:bg-[#F4F4F5] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
          >
            進め方を詳しく見る
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
