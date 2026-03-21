const rows = [
  { label: "法人名／屋号", value: "（要確認）" },
  { label: "代表者", value: "（要確認）" },
  { label: "所在地", value: "（要確認：鹿児島市周辺想定）" },
  { label: "メール", value: "（要確認）" },
  { label: "電話", value: "（公開可否：要確認）" },
];

export default function KgsAboutCompanyTableSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-about-table-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-about-table-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          事業者情報（表形式）
        </h2>
        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[280px] border-collapse border border-[#E4E4E7] bg-[#FFFFFF] text-left text-sm text-[#18181B]">
            <tbody>
              {rows.map((r) => (
                <tr key={r.label} className="border-b border-[#E4E4E7]">
                  <th
                    scope="row"
                    className="w-[40%] border-r border-[#E4E4E7] bg-[#FAFAF9] px-4 py-3 font-semibold"
                  >
                    {r.label}
                  </th>
                  <td className="px-4 py-3">{r.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 max-w-prose text-left text-sm text-[#52525B]">
          正式な法人名・屋号・代表者名・所在地・電話・メールの公開可否は未確定のため、公開文案は確定後に差し替えます。
        </p>
      </div>
    </section>
  );
}
