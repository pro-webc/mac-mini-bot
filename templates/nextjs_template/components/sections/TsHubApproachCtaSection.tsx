import CtaButton from "@/components/CtaButton";

export default function TsHubApproachCtaSection() {
  return (
    <section className="bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="border border-[#E4E4E7] bg-[#FFFFFF] p-6 sm:p-10">
          <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
            進行イメージを自社に当てはめて確認する
          </h2>
          <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
            人数・車両運用・日程について、分かる範囲でお聞かせください。
          </p>
          <div className="mt-8">
            <CtaButton href="/contact">無料で相談する</CtaButton>
          </div>
        </div>
      </div>
    </section>
  );
}
