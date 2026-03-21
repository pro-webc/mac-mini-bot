import Link from "next/link";
import { ArrowRight } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import { BOOKING_URL } from "@/lib/bookingUrl";

export default function TshServiceCtaSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="service-cta-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="service-cta-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          内容を具体化したい方へ
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          当日イメージはプログラムページ、ご相談はフォームまたは予約からどうぞ。
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
        <ul className="mt-10 flex flex-col gap-3">
          <li>
            <Link
              href="/program"
              className="inline-flex min-h-[44px] items-center gap-2 text-base font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            >
              当日の流れはこちら
              <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            </Link>
          </li>
          <li>
            <Link
              href="/faq"
              className="inline-flex min-h-[44px] items-center gap-2 text-base font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            >
              質問があればFAQ
              <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            </Link>
          </li>
        </ul>
      </div>
    </section>
  );
}
