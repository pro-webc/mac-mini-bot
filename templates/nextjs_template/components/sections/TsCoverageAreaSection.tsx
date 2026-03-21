import { MapPin } from "lucide-react";

export default function TsCoverageAreaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="coverage-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="coverage-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          対応エリア
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <MapPin className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              主に鹿児島市周辺（詳細半径は相談）
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <MapPin className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              遠方はオンライン要素の併用可否を個別に検討
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
