import CtaButton from "@/components/CtaButton";

export default function TsHubStdServicesCtaSection() {
  return (
    <section
      className="bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="services-cta-heading"
    >
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2
          id="services-cta-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          内容のすり合わせから始められます
        </h2>
        <p className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          既存の教育資料がなくても構いません。社内の運用実態から設計します。
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
