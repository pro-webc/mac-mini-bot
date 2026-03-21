export default function TrafficAboutCompanyTableSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-company-table-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-company-table-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          会社情報（確定値は後日）
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-relaxed text-[#52525B]">
          法人名・屋号、所在地、連絡先、受付時間は「調整中」と明示。
        </p>
        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[280px] border-collapse border border-[#E4E4E7] bg-[#FFFFFF] text-left text-sm text-[#18181B] md:text-base">
            <tbody>
              <tr className="border-b border-[#E4E4E7]">
                <th
                  scope="row"
                  className="w-[40%] border-r border-[#E4E4E7] bg-[#FAFAF9] px-4 py-3 font-semibold"
                >
                  法人名・屋号
                </th>
                <td className="px-4 py-3">調整中</td>
              </tr>
              <tr className="border-b border-[#E4E4E7]">
                <th
                  scope="row"
                  className="border-r border-[#E4E4E7] bg-[#FAFAF9] px-4 py-3 font-semibold"
                >
                  所在地
                </th>
                <td className="px-4 py-3">調整中（鹿児島市を中心とした周辺エリア）</td>
              </tr>
              <tr className="border-b border-[#E4E4E7]">
                <th
                  scope="row"
                  className="border-r border-[#E4E4E7] bg-[#FAFAF9] px-4 py-3 font-semibold"
                >
                  連絡先
                </th>
                <td className="px-4 py-3">調整中</td>
              </tr>
              <tr>
                <th
                  scope="row"
                  className="border-r border-[#E4E4E7] bg-[#FAFAF9] px-4 py-3 font-semibold"
                >
                  受付時間
                </th>
                <td className="px-4 py-3">調整中</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
