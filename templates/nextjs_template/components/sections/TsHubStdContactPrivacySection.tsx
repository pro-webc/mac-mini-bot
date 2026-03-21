export default function TsHubStdContactPrivacySection() {
  return (
    <section
      id="privacy"
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="privacy-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="privacy-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          個人情報の取扱い
        </h2>
        <div className="mt-8 max-w-prose space-y-4 text-left text-sm leading-relaxed text-[#0F172A]">
          <p>
            取得する情報：お問い合わせフォームにご入力いただいた会社名、氏名、メールアドレス、電話番号、役職・担当、お問い合わせ内容など。
          </p>
          <p>
            利用目的：お問い合わせへの回答、ご連絡、サービスご提案に必要な確認。目的外利用はしません。
          </p>
          <p>
            第三者提供：法令に基づく場合を除き、本人の同意なく第三者に提供しません。
          </p>
          <p>
            保管期間：対応完了後、合理的な期間を経た後に削除します（社内規程に従います）。
          </p>
          <p>
            開示・訂正・削除等のご請求：お問い合わせフォームよりご連絡ください。
          </p>
          <p className="text-[#64748B]">
            本内容は一般的な枠組みの説明です。確定稿はクライアント確認後に差し替え可能です。
          </p>
        </div>
      </div>
    </section>
  );
}
