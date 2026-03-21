export default function TsLegalPlaceholderSection() {
  return (
    <section className="bg-[#F4F4F5] py-16 md:py-20" aria-labelledby="legal-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="legal-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          会社概要・表記（準備中）
        </h2>
        <div className="mt-8 overflow-x-auto rounded-none border border-[#E4E4E7] bg-[#FFFFFF]">
          <table className="w-full min-w-[280px] border-collapse text-left text-sm text-[#18181B]">
            <caption className="sr-only">会社概要（準備中）</caption>
            <tbody>
              <tr className="border-b border-[#E4E4E7]">
                <th
                  scope="row"
                  className="w-[40%] border-r border-[#E4E4E7] bg-[#FAFAF9] p-3 font-semibold md:p-4"
                >
                  屋号／法人形態／代表者表記
                </th>
                <td className="p-3 md:p-4">要確定</td>
              </tr>
              <tr className="border-b border-[#E4E4E7]">
                <th
                  scope="row"
                  className="border-r border-[#E4E4E7] bg-[#FAFAF9] p-3 font-semibold md:p-4"
                >
                  所在地／電話／メール
                </th>
                <td className="p-3 md:p-4">公開範囲を要確認</td>
              </tr>
              <tr>
                <th
                  scope="row"
                  className="border-r border-[#E4E4E7] bg-[#FAFAF9] p-3 font-semibold md:p-4"
                >
                  備考
                </th>
                <td className="p-3 md:p-4">
                  ※確定後、tableもしくはdlで掲載
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <ul className="mt-6 space-y-2 text-left text-sm text-[#52525B]">
          <li>屋号／法人形態／代表者表記：要確定</li>
          <li>所在地／電話／メール：公開範囲を要確認</li>
          <li>※確定後、tableもしくはdlで掲載</li>
        </ul>
      </div>
    </section>
  );
}
