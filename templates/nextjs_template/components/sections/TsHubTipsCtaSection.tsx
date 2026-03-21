import CtaButton from "@/components/CtaButton";

export default function TsHubTipsCtaSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-6 sm:p-10">
          <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
            現場の課題に合わせたネタ設計も相談できます
          </h2>
          <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
            業務特性に合わせて短時間の設計相談も可能です。
          </p>
          <div className="mt-8">
            <CtaButton href="/contact">自社向けにネタを組み立てたい</CtaButton>
          </div>
        </div>
      </div>
    </section>
  );
}
