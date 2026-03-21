import CtaButton from "@/components/CtaButton";
import { BOOKING_URL } from "@/lib/bookingUrl";

export default function TshHomeFinalCtaSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="final-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6 md:py-20">
        <h2
          id="final-cta-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          まずは15分、状況整理から
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          導入判断は急がなくて大丈夫です。課題の整理と、実施の選択肢だけでもお返しします。
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <CtaButton href={BOOKING_URL}>相談予約を取る</CtaButton>
          <CtaButton
            href="/contact"
            className="!bg-[#ffffff] !text-[#0f766e] ring-2 ring-inset ring-[#0f766e] hover:!bg-[#f5f5f4] focus-visible:!outline-[#0f766e]"
          >
            お問い合わせフォームへ
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
