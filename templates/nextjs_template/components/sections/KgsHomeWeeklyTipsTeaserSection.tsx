import Link from "next/link";
import { BookOpen } from "lucide-react";

export default function KgsHomeWeeklyTipsTeaserSection() {
  const items = [
    "短時間で読めるチェック観点・問いかけ例・共有テンプレの切り口を週次更新（運用は月次修正枠と整合）",
    "担当者がそのまま社内共有に転用しやすい言い回しを意識",
    "更新一覧は専用ページへ",
  ];

  const linkClass =
    "inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#1D4ED8] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:border-[#1E40AF] hover:bg-[#F4F4F5] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] motion-safe:transition-colors";

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-home-tips-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-tips-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          毎週の「一口アドバイス」で、朝礼のネタ不足を減らす
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
        <div className="mt-10">
          <Link href="/tips" className={`${linkClass} w-full sm:w-auto`}>
            <BookOpen className="h-5 w-5 shrink-0" aria-hidden />
            一口アドバイスを読む
          </Link>
        </div>
      </div>
    </section>
  );
}
