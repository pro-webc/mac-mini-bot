export default function PricingTableSection() {
  return (
    <section
      className="overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="pricing-table-heading"
    >
      <h2 id="pricing-table-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        料金表（確定値は別途反映）
      </h2>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[320px] border-collapse border border-[#E2E8F0] text-left text-sm text-[#475569]">
          <caption className="mb-2 text-left text-xs font-semibold text-[#64748B]">
            金額・項目名は仮置きです。確定後に置き換えます。
          </caption>
          <thead>
            <tr className="bg-[#F1F5F9]">
              <th scope="col" className="border border-[#E2E8F0] p-3 font-bold text-[#0F172A]">
                項目
              </th>
              <th scope="col" className="border border-[#E2E8F0] p-3 font-bold text-[#0F172A]">
                単位
              </th>
              <th scope="col" className="border border-[#E2E8F0] p-3 font-bold text-[#0F172A]">
                目安（税込・仮）
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border border-[#E2E8F0] p-3">現地調査・出張費</td>
              <td className="border border-[#E2E8F0] p-3">1回</td>
              <td className="border border-[#E2E8F0] p-3">◯,◯◯◯円〜</td>
            </tr>
            <tr className="bg-[#F8FAFC]">
              <td className="border border-[#E2E8F0] p-3">標準交換作業（仮称）</td>
              <td className="border border-[#E2E8F0] p-3">1式</td>
              <td className="border border-[#E2E8F0] p-3">◯◯,◯◯◯円〜</td>
            </tr>
            <tr>
              <td className="border border-[#E2E8F0] p-3">部材費（一般的なパーツ）</td>
              <td className="border border-[#E2E8F0] p-3">実費</td>
              <td className="border border-[#E2E8F0] p-3">見積時に内訳提示</td>
            </tr>
            <tr className="bg-[#F8FAFC]">
              <td className="border border-[#E2E8F0] p-3">急行・時間外対応</td>
              <td className="border border-[#E2E8F0] p-3">1式</td>
              <td className="border border-[#E2E8F0] p-3">別途オプション</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
