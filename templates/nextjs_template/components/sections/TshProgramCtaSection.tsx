import CtaButton from "@/components/CtaButton";
import { BOOKING_URL } from "@/lib/bookingUrl";

export default function TshProgramCtaSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="prog-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="prog-cta-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          実施イメージを社内共有したい方へ
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          希望日程の目安でも構いません。まずはお聞かせください。
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <CtaButton href={BOOKING_URL}>相談予約を取る</CtaButton>
          <CtaButton
            href="/contact"
            className="!bg-[#ffffff] !text-[#0f766e] ring-2 ring-inset ring-[#0f766e] hover:!bg-[#f5f5f4] focus-visible:!outline-[#0f766e]"
          >
            お問い合わせする
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
