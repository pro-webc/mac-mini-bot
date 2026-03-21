export default function TsHubStdContactFormIntroSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-12 md:py-14"
      aria-labelledby="form-intro-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="form-intro-heading"
          className="text-xl font-semibold text-[#0F172A] md:text-2xl"
        >
          送信前にご確認ください
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          個人情報はお問い合わせ対応のために利用し、目的外利用はしません（詳細は下部の取扱いをご確認ください）。
        </p>
        <p className="mt-3 text-sm text-[#64748B]">
          必須項目はラベルで明示しています。内容が未定の項目は「未定」とご入力ください。
        </p>
      </div>
    </section>
  );
}
