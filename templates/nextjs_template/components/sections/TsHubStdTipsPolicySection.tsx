export default function TsHubStdTipsPolicySection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="tips-policy-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="tips-policy-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          ご利用上の留意点
        </h2>
        <div className="mt-8 max-w-prose rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-6">
          <p className="text-left text-base leading-[1.7] text-[#0F172A]">
            ここで紹介する内容は一般論です。各社の規程・路線条件・車両特性に合わせて判断してください。
          </p>
          <p className="mt-4 text-left text-base leading-[1.7] text-[#0F172A]">
            法令解釈の最終判断は、管轄当局の指導および社内規程に従ってください。
          </p>
        </div>
      </div>
    </section>
  );
}
