import Link from "next/link";
import { MessageCircle } from "lucide-react";

type Props = {
  /** お問い合わせページでは自己参照を避け、視覚的なプレースホルダのみ表示 */
  variant?: "default" | "contactPage";
};

export default function ContactLineNoteSection({ variant = "default" }: Props) {
  const body = (
    <>
      <h2 id="line-heading" className="text-xl font-bold text-white md:text-2xl">
        LINE公式アカウント（二次の相談窓口）
      </h2>
      <p className="mt-4 text-left text-sm leading-relaxed text-[#E0E7FF]">
        フォームが難しい場合は、LINE公式アカウントからもお問い合わせいただけます（URL・QRは確定後に設定）。公開URLのプレースホルダ：
        <span className="ml-1 font-mono text-[#caeb25]">LINE_OFFICIAL_URL_PLACEHOLDER</span>
      </p>
    </>
  );

  if (variant === "contactPage") {
    return (
      <section
        id="line-guide"
        className="mt-12 scroll-mt-28 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
        aria-labelledby="line-heading"
      >
        {body}
        <div className="mt-6 inline-flex min-h-[48px] min-w-[44px] items-center gap-2 rounded-[14px] border-2 border-dashed border-white/50 bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#E0E7FF]">
          <MessageCircle className="h-5 w-5 text-[#caeb25]" aria-hidden />
          LINEでも相談（URL準備中）
        </div>
      </section>
    );
  }

  return (
    <section
      id="line-guide"
      className="mt-12 scroll-mt-28 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="line-heading"
    >
      {body}
      <div className="mt-6">
        <Link
          href="/contact#line-guide"
          className="inline-flex min-h-[48px] min-w-[44px] items-center gap-2 rounded-[14px] border-2 border-[#caeb25] bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#caeb25] transition-colors hover:bg-[#1d4ed8] hover:text-white active:bg-[#1e40af] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          <MessageCircle className="h-5 w-5" aria-hidden />
          LINEでも相談（URL準備中）
        </Link>
      </div>
    </section>
  );
}
