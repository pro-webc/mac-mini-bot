import { HeartHandshake } from "lucide-react";

export default function TsHubApproachPhilosophySection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <HeartHandshake
            className="h-8 w-8 shrink-0 text-[#1D4ED8]"
            aria-hidden
          />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              なぜ「押しつけ」に見えない進行にするのか
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              安全は続く習慣が本体です。当事者の言葉が組織に残るよう、正解を一方的に渡すのではなく、現場が判断できる材料と言葉を揃えます。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
