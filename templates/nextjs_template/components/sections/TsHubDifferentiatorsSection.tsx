import { Briefcase, Handshake, Layers } from "lucide-react";

export default function TsHubDifferentiatorsSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="diff-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="diff-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          なぜ「話しただけ」で終わりにくいのか
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:gap-6">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center border border-[#E4E4E7] bg-[#FAFAF9]">
                <Briefcase className="h-6 w-6 text-[#0F766E]" aria-hidden />
              </div>
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                交通関連業務に長く従事したうえでの独立（約30年に近い専門経験の方向性）
              </p>
            </div>
          </li>
          <li className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:gap-6">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center border border-[#E4E4E7] bg-[#FAFAF9]">
                <Handshake className="h-6 w-6 text-[#0F766E]" aria-hidden />
              </div>
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                事故現場経験、企業側担当者の声を踏まえた課題設定
              </p>
            </div>
          </li>
          <li className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:gap-6">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center border border-[#E4E4E7] bg-[#FAFAF9]">
                <Layers className="h-6 w-6 text-[#0F766E]" aria-hidden />
              </div>
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                警察対応の話だけに見えないよう、仕組みで説明負荷を下げる
              </p>
            </div>
          </li>
        </ul>
        <div
          className="mt-10 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6"
          aria-hidden
        >
          <p className="text-center text-xs font-semibold uppercase tracking-wide text-[#52525B]">
            図解イメージ（マークアップ）
          </p>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-center text-sm text-[#18181B]">
              経験の文脈
            </div>
            <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-center text-sm text-[#18181B]">
              現場の言葉
            </div>
            <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-center text-sm text-[#18181B]">
              仕組みで再現
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
