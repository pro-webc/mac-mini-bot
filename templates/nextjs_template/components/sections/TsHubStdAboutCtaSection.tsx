import CtaButton from "@/components/CtaButton";

export default function TsHubStdAboutCtaSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="about-cta-heading">
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2
          id="about-cta-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          社内説明用に、資料化もご相談ください
        </h2>
        <p className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          概要スライドの要望があれば、相談内容に合わせて構成案を提案します。
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            お問い合わせへ
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
