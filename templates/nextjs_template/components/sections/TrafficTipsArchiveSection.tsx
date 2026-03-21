import Link from "next/link";
import { ArrowRight, Newspaper } from "lucide-react";

const articles = [
  {
    date: "2025-03-10",
    tag: "管理者向け",
    summary:
      "短時間の朝礼で「観点1つ＋問い1つ」に絞ると、現場の発言が増えやすい。",
  },
  {
    date: "2025-03-03",
    tag: "現場向け",
    summary:
      "合流・車線変更の前に「後方確認のタイミング」を言語化して振り返る。",
  },
  {
    date: "2025-02-24",
    tag: "管理者向け",
    summary:
      "週次のネタは「再現できる行動」に落とす：チェック観点を3つに固定する。",
  },
];

export default function TrafficTipsArchiveSection() {
  return (
    <section
      id="tips-archive"
      className="scroll-mt-28 border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-tips-archive-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Newspaper className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <h2
            id="traffic-tips-archive-heading"
            className="text-left font-semibold leading-[1.35] text-[#18181B]"
            style={{
              fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
              fontWeight: 650,
            }}
          >
            アーカイブ（デモ記事3本）
          </h2>
        </div>
        <ul className="mt-10 grid gap-4 md:grid-cols-3">
          {articles.map((a) => (
            <li
              key={a.date}
              className="flex flex-col justify-between rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-5"
            >
              <div>
                <p className="text-left text-xs font-medium text-[#52525B]">
                  {a.date}
                </p>
                <span className="mt-2 inline-block rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] px-2 py-1 text-xs font-semibold text-[#0F766E]">
                  {a.tag}
                </span>
                <p className="mt-3 text-left text-base leading-relaxed text-[#18181B]">
                  {a.summary}
                </p>
              </div>
            </li>
          ))}
        </ul>
        <div className="mt-10">
          <Link
            href="/contact"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            お問い合わせ（カスタムネタの相談）
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
