import { Building2, Truck, Users } from "lucide-react";

export default function TsHubAudienceSegmentsSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="audience-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="audience-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          想定している支援の入り口
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-4 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
            <Building2 className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <div>
              <h3 className="text-base font-semibold text-[#18181B]">
                当面の主な入り口
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                社用車を白ナンバーで運用する企業の管理部門
              </p>
            </div>
          </li>
          <li className="flex gap-4 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
            <Truck className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <div>
              <h3 className="text-base font-semibold text-[#18181B]">
                将来的な展開
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                緑ナンバー等の運輸・タクシー・トラック事業者領域
              </p>
            </div>
          </li>
          <li className="flex gap-4 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
            <Users className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <div>
              <h3 className="text-base font-semibold text-[#18181B]">
                規模の目安
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                車両台数が多い企業ほど、管理設計の効果が出やすい（目安：20台以上を優先しつつ要相談）
              </p>
            </div>
          </li>
        </ul>
      </div>
    </section>
  );
}
