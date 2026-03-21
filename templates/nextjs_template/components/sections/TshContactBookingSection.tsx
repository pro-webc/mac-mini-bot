import CtaButton from "@/components/CtaButton";
import { BOOKING_URL } from "@/lib/bookingUrl";

export default function TshContactBookingSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="contact-booking-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="contact-booking-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          面談・相談の予約（推奨）
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          外部予約ツールへ移動します。URLは運用で差し替え可能です。
        </p>
        <div className="mt-8">
          <CtaButton href={BOOKING_URL}>面談・相談を予約する</CtaButton>
        </div>
      </div>
    </section>
  );
}
