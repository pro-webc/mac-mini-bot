import Link from "next/link";
import { ChevronRight, Mail } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function HomeClosingCtaSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#caeb25]/40 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="closing-cta-heading"
    >
      <h2
        id="closing-cta-heading"
        className="text-center text-xl font-bold text-white md:text-2xl"
      >
        まずは状況を聞かせてください
      </h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-base leading-relaxed text-[#BFDBFE] md:text-left">
        設備種別が未確定でも構いません。現場写真や図面がなくても、打合せしながら整理できます。LINE公式は「準備中」ではなく、URL提供後にボタンを設置します。
      </p>
      <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <CtaButton href="/contact">
          <span className="inline-flex items-center gap-2">
            <Mail className="h-5 w-5" aria-hidden />
            フォームから相談する
            <ChevronRight className="h-5 w-5" aria-hidden />
          </span>
        </CtaButton>
        <span
          className="inline-flex min-h-[48px] min-w-[44px] cursor-not-allowed items-center justify-center gap-2 rounded-full border-2 border-white/40 bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#E0E7FF] opacity-80"
          aria-disabled="true"
        >
          LINEで相談（URL提供後に連携）
        </span>
      </div>
      <p className="mt-4 text-center text-xs text-[#93C5FD] sm:text-left">
        お問い合わせを最優先でご案内しています。フォームは{" "}
        <Link
          href="/contact"
          className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          お問い合わせページ
        </Link>
        から。
      </p>
    </section>
  );
}
