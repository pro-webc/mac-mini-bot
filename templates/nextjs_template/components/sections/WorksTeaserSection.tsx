import Link from "next/link";
import { ChevronRight, Mail } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function WorksTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#caeb25]/40 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="works-cta-heading"
    >
      <h2
        id="works-cta-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        類似案件の相談
      </h2>
      <p className="mt-3 max-w-2xl text-left text-base leading-relaxed text-[#BFDBFE]">
        掲載事例が未整備でも、画像や図面があれば事前ヒアリングが進めやすくなります。まずはお問い合わせください。
      </p>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        <CtaButton href="/contact">
          <span className="inline-flex items-center gap-2">
            <Mail className="h-5 w-5" aria-hidden />
            お問い合わせフォーム
            <ChevronRight className="h-5 w-5 fill-current" aria-hidden />
          </span>
        </CtaButton>
        <Link
          href="tel:0669745788"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center rounded-[14px] border-2 border-white bg-[#2563eb] px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-[#1d4ed8] active:bg-[#1e3a8a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          06-6974-5788
        </Link>
      </div>
    </section>
  );
}
