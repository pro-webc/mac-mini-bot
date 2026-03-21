import { List, ExternalLink } from "lucide-react";

export default function TsContactIntroSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="contact-intro-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="contact-intro-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          送信前に読むとスムーズ
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
            <List className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              相談内容は箇条書きで構いません（現状・人数・希望時期）
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
            <ExternalLink className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              予約はフォーム後に外部ツールへ進みます
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
