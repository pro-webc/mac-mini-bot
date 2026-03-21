import CtaButton from "@/components/CtaButton";
import Link from "next/link";

export default function TsHubStdProcessOnlineSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="online-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="online-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          オンライン対応について
        </h2>
        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <div className="max-w-prose rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6">
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              初回の打ち合わせやフォローはオンライン（Zoom等）に対応します。
            </p>
            <p className="mt-4 text-left text-base leading-[1.7] text-[#0F172A]">
              実車を伴う評価や現地集合が適切な場合は、安全と法令遵守を優先して計画します。
            </p>
          </div>
          <div className="flex flex-col justify-center gap-4 border border-[#E2E8F0] bg-[#FFFFFF] p-6">
            <Link
              href="/tips"
              className="inline-flex min-h-[44px] items-center text-sm font-semibold text-[#0F766E] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
            >
              一口アドバイスを読む
            </Link>
            <CtaButton href="/contact" className="w-full justify-center !min-h-[44px]">
              お問い合わせへ
            </CtaButton>
          </div>
        </div>
      </div>
    </section>
  );
}
