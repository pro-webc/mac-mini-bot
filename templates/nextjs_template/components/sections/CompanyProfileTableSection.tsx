export default function CompanyProfileTableSection() {
  const rows: { label: string; value: string; isEmail?: boolean }[] = [
    { label: "社名", value: "株式会社ワン・ピース" },
    { label: "代表者", value: "代表取締役 米倉 豊" },
    { label: "所在地", value: "〒545-0052 大阪市阿倍野区三明町2丁目16-5" },
    { label: "電話番号", value: "06-6974-5788" },
    { label: "メール", value: "yy-yumi@task888.com", isEmail: true },
    { label: "営業時間", value: "9:00〜18:00" },
    { label: "従業員数", value: "6名" },
    { label: "設立", value: "要確認（掲載は確定後）" },
  ];

  return (
    <section
      className="overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="company-profile-heading"
    >
      <h2
        id="company-profile-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        会社概要
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        設立年月・資本金等は未確定のため、確定後に追記または差し替えます。
      </p>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[320px] border-collapse border border-[#E2E8F0] text-left text-sm">
          <tbody className="text-[#475569]">
            {rows.map((row) => (
              <tr key={row.label}>
                <th
                  scope="row"
                  className="w-40 border border-[#E2E8F0] bg-[#F1F5F9] p-3 font-bold text-[#0F172A]"
                >
                  {row.label}
                </th>
                <td className="border border-[#E2E8F0] p-3 text-[#475569]">
                  {row.isEmail ? (
                    <a
                      href={`mailto:${row.value}`}
                      className="font-medium text-[#2563eb] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                    >
                      {row.value}
                    </a>
                  ) : (
                    row.value
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
