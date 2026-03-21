import CtaButton from "@/components/CtaButton";

export default function TsHubStdProcessCtaSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="process-cta-heading">
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2
          id="process-cta-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          日程と形式は一緒に決めます
        </h2>
        <p className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          まずは希望の時期と、社内で困っている点を送ってください。
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            お問い合わせフォームへ
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
