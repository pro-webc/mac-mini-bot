import { CalendarClock } from "lucide-react";

export default function TsBookingSecondarySection() {
  return (
    <section
      id="booking-external"
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="booking-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="booking-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          日程調整（外部ツール）
        </h2>
        <ul className="mt-8 space-y-4 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
          <li className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            TimeRex等：アカウントはクライアント側で作成し、URLをサイトに設置
          </li>
          <li className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            フォームと予約の役割分担は運用で調整
          </li>
        </ul>
        <p className="mt-6 text-left text-sm text-[#52525B]">
          フォーム送信後に案内しても、先に予約だけでも可（運用で決定）
        </p>
        <div className="mt-8">
          <button
            type="button"
            disabled
            className="inline-flex min-h-[44px] cursor-not-allowed items-center justify-center gap-2 rounded-[12px] border-2 border-[#A1A1AA] bg-[#F4F4F5] px-6 py-3 text-base font-semibold text-[#52525B]"
            aria-describedby="booking-url-note"
          >
            <CalendarClock className="h-5 w-5" aria-hidden />
            予約ページを開く
          </button>
          <p id="booking-url-note" className="mt-2 text-left text-sm text-[#52525B]">
            ※外部予約ツールのURLは確定後に有効化します。
          </p>
        </div>
      </div>
    </section>
  );
}
