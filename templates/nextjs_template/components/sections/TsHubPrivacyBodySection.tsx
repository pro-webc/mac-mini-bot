const blocks = [
  {
    h2: "取得する情報",
    body: "氏名、会社名、部署、電話番号、メールアドレス、お問い合わせ内容、その他ご入力いただいた情報。",
  },
  {
    h2: "利用目的",
    body: "お問い合わせ対応、ご連絡、サービス提供に関する必要な確認、記録管理、法令に基づく対応。",
  },
  {
    h2: "第三者提供",
    body: "法令に基づく場合を除き、本人の同意なく第三者に提供しません。",
  },
  {
    h2: "委託",
    body: "予約・フォーム等の外部サービスを利用する場合、委託先における管理について必要な契約を締結します。",
  },
  {
    h2: "開示等の請求",
    body: "ご本人からの求めに応じ、法令に従い対応します。手続きはお問い合わせ窓口へご連絡ください。",
  },
  {
    h2: "改定",
    body: "法令や実務の変更に応じて本ページを更新します。",
  },
];

export default function TsHubPrivacyBodySection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
          本文
        </h2>
        <div className="mt-10 space-y-10">
          {blocks.map(({ h2, body }) => (
            <div key={h2}>
              <h3 className="text-left text-lg font-semibold text-[#18181B]">
                {h2}
              </h3>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
