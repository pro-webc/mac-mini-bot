import Link from "next/link";
import { ArrowRight, Lightbulb } from "lucide-react";

export default function TrafficTipsFeaturedSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-featured-tip-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <h2
            id="traffic-featured-tip-heading"
            className="text-left font-semibold leading-[1.35] text-[#18181B]"
            style={{
              fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
              fontWeight: 650,
            }}
          >
            今週の一口アドバイス（デモ）
          </h2>
        </div>
        <p className="mt-4 text-left text-sm text-[#52525B] md:ml-9">
          見出し例：「発進前の“ひと呼吸”で、見落としを減らす」
        </p>
        <div className="mt-8 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-6 md:ml-9 md:max-w-prose">
          <h3 className="text-left text-lg font-semibold leading-[1.45] text-[#18181B]">
            発進前の“ひと呼吸”で、見落としを減らす
          </h3>
          <div className="mt-4 space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
            <p>
              急いでいるほど、確認が抜けやすい場面があります。発進前に短い停止を挟み、視線の順序をそろえるだけでも、見落としリスクを下げやすくなります。
            </p>
            <p>
              朝礼での問いかけ例：「昨日、確認が薄くなりがちだったのはどの場面？」
            </p>
            <p>
              朝礼での問いかけ例：「発進前の“ひと呼吸”は、今日はどの場面から試せそうですか？」
            </p>
            <p>
              チェック観点：周辺確認の順序／合図のタイミング／車間の取り方
            </p>
          </div>
          <p className="mt-6 text-left text-sm leading-relaxed text-[#52525B]">
            ※一般論です。現場ルールは貴社規程を優先してください。
          </p>
        </div>
        <div className="mt-10 md:ml-9">
          <Link
            href="#tips-archive"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            過去のネタを見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
