import { BookOpen, RefreshCw, MapPinned } from "lucide-react";

export default function TsHubTrustStripSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="trust-strip-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="trust-strip-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          このサイトで得られること
        </h2>
        <ul className="mt-8 grid gap-4 md:grid-cols-3">
          <li className="flex flex-col gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <RefreshCw className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              週1回の短いアドバイスで、朝礼ネタと現場の話題を補助
            </p>
          </li>
          <li className="flex flex-col gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <BookOpen className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              営業後にサイトで手順と考え方を再確認できる
            </p>
          </li>
          <li className="flex flex-col gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <MapPinned className="h-8 w-8 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              全国大量集客ではなく、地域の担当者向けに誤解なく説明する
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
