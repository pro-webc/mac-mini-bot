import Link from "next/link";
import CtaButton from "@/components/CtaButton";

export default function TsHubPrivacyContactFooterSection() {
  return (
    <section className="bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="border border-[#E4E4E7] bg-[#FFFFFF] p-6 sm:p-10">
          <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
            お問い合わせ窓口
          </h2>
          <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
            個人情報の取り扱いに関するお問い合わせは、フォームからご連絡ください。
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href="/contact">お問い合わせフォームへ</CtaButton>
            <Link
              href="/"
              className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center rounded-[12px] border-2 border-[#1D4ED8] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:bg-[#EFF6FF] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            >
              トップへ戻る
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
