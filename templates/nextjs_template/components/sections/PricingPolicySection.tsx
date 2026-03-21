import CtaButton from "@/components/CtaButton";

export default function PricingPolicySection() {
  return (
    <section className="bg-[#F8FAFC] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          料金・お見積りの方針
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          料金表をサイト上に公開するかどうかは運用方針の確定待ちです。内容がばらつく案件については、現地確認後の個別お見積りを基本とする見込みです。断言できる範囲が決まり次第、本ページに追記します。
        </p>
        <div className="mt-8 rounded-[20px] border border-[#0284C7] bg-[#FFFFFF] p-8 text-center">
          <p className="text-lg font-semibold text-[#0F172A]">
            まずは状況をお聞きしたうえで、見積りの進め方をご案内します
          </p>
          <div className="mt-6 flex justify-center">
            <CtaButton href="/contact">個別見積の相談へ</CtaButton>
          </div>
        </div>
      </div>
    </section>
  );
}
