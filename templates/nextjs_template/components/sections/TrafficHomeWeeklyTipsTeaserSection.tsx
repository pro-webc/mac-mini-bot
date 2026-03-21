import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

export default function TrafficHomeWeeklyTipsTeaserSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-weekly-tips-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Sparkles className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <div className="min-w-0 flex-1">
            <h2
              id="traffic-weekly-tips-heading"
              className="text-left font-semibold leading-[1.35] text-[#18181B]"
              style={{
                fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
                fontWeight: 650,
              }}
            >
              週次の「一口アドバイス」コーナー（運用）
            </h2>
            <div className="mt-4 max-w-[65ch] space-y-3 text-left text-base leading-[1.75] text-[#52525B]">
              <p>
                安全担当者がその週の朝礼で使える短いネタを更新（月5回までの修正枠を想定）
              </p>
              <p>
                事故の教訓を煽らず、再現性のある観点・チェックに落とす
              </p>
              <p>最新記事は一覧ページへ</p>
            </div>
          </div>
        </div>
        <div className="mt-10">
          <Link
            href="/tips"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            朝礼ネタ一覧を見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
