"use client";

import { Calendar } from "lucide-react";

export default function TsHubStdContactBookingSection() {
  return (
    <section
      id="booking"
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="booking-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="booking-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          日程を選んで相談（任意）
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          オンライン初回面談をご希望の方は、予約ページから日程をお選びください。URLは運用準備が整い次第、こちらに設定します。
        </p>
        <button
          type="button"
          className="mt-8 inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] hover:bg-[#F0FDFA] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          onClick={() => {
            const el = document.getElementById("booking-note");
            el?.focus();
          }}
        >
          <Calendar className="h-5 w-5 shrink-0" aria-hidden />
          日程を選ぶ
        </button>
        <p
          id="booking-note"
          tabIndex={-1}
          className="mt-6 max-w-prose text-left text-sm text-[#64748B] outline-none"
        >
          現在はフォーム送信で日程調整を承ります。外部予約ツールのリンクは、公開情報として整備後に本セクションへ追加します。
        </p>
      </div>
    </section>
  );
}
