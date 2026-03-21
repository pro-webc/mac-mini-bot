import { BadgeCheck } from "lucide-react";

export default function TshProgramInstructorSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="instructor-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="instructor-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          講師について（確認済みの範囲）
        </h2>
        <div className="mt-6 flex gap-4 border border-[#e7e5e4] bg-[#ffffff] p-5">
          <BadgeCheck
            className="h-8 w-8 shrink-0 text-[#0f766e]"
            aria-hidden
          />
          <p className="max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
            講師は、交通関連の現場経験が長年にわたり、事故現場の経験も踏まえた説明が可能です。表現は教育目的に留め、過度な刺激にはしません。受講社数や認定等の数値実績は未確定のため、サイト上では掲載しません。
          </p>
        </div>
      </div>
    </section>
  );
}
