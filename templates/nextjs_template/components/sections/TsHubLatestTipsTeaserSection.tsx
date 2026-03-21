import Link from "next/link";
import { ChevronRight, Lightbulb } from "lucide-react";

const examples = [
  "【デモ】今日の朝礼：出庫前に「ブレーキとタイヤ」を一言で確認する",
  "【デモ】週次ミーティング：先週の「ヒヤリ」を1件だけ共有する時間を固定する",
  "【デモ】新人配属：先輩が同乗デブリーフの質問テンプレを使う",
];

export default function TsHubLatestTipsTeaserSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="tips-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="tips-teaser-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          週1の一口アドバイス（最新）
        </h2>
        <ul className="mt-8 space-y-3">
          {examples.map((text) => (
            <li
              key={text}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4"
            >
              <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]" aria-hidden />
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                {text}
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-left text-sm text-[#52525B]">
          ※掲載開始後、実記事に差し替え
        </p>
        <div className="mt-8">
          <Link
            href="/tips"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
          >
            アドバイス一覧を見る
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
