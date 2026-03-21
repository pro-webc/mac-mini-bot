import CtaButton from "@/components/CtaButton";

export default function TsHubStdHomeFinalCtaSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#0F766E] py-16 md:py-20"
      aria-labelledby="final-cta-heading"
    >
      <div className="mx-auto max-w-3xl px-4 text-center md:px-6">
        <h2
          id="final-cta-heading"
          className="text-2xl font-semibold text-[#F8FAFC] md:text-3xl"
        >
          まずは状況をお聞かせください
        </h2>
        <p className="mx-auto mt-6 max-w-prose text-left text-base leading-[1.7] text-[#E2E8F0] md:text-center">
          課題の輪郭がまだ曖昧でも問題ありません。無料相談から、実施形式と次の一歩まで一緒に整理します。
        </p>
        <div className="mt-10 flex justify-center">
          <CtaButton
            href="/contact"
            className="w-full max-w-md justify-center !bg-[#F8FAFC] !text-[#0F766E] hover:!bg-[#E2E8F0] active:!bg-[#CBD5E1] focus-visible:outline-[#F8FAFC]"
          >
            お問い合わせフォームへ
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
