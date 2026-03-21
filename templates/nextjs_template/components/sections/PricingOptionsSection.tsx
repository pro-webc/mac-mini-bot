export default function PricingOptionsSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="pricing-options-heading"
    >
      <h2 id="pricing-options-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        オプション・追加費用の例（確定待ち）
      </h2>
      <ul className="mt-4 list-inside list-disc space-y-2 text-left text-sm leading-relaxed text-[#475569]">
        <li>高所作業や狭所作業に伴う追加人員</li>
        <li>既存部材の撤去処分費</li>
        <li>メーカー指定外の高級パーツへの変更差額</li>
        <li>再訪・再調整が発生した場合の出張費（条件は契約書面で確定）</li>
      </ul>
      <p className="mt-4 rounded-none border border-dashed border-[#CBD5E1] bg-[#F8FAFC] p-3 text-xs leading-relaxed text-[#64748B]">
        公開する料金体系の最終版が決まり次第、箇条書きと表の双方を同期して更新します。
      </p>
    </section>
  );
}
