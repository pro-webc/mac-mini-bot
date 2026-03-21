import CtaButton from "@/components/CtaButton";
import Link from "next/link";

export default function TsHubStdHomeTrustSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="trust-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="trust-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          運営・対応について
        </h2>
        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <div className="max-w-prose rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-6">
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              講師と窓口は原則同一のため、ご要望の伝達が分断されにくい体制です。
            </p>
            <p className="mt-4 text-left text-base leading-[1.7] text-[#0F172A]">
              対応エリアは鹿児島市周辺を中心に、事前に範囲と実施方法をすり合わせます。
            </p>
          </div>
          <div className="flex flex-col justify-center gap-4 border border-[#E2E8F0] bg-[#FFFFFF] p-6">
            <p className="text-sm text-[#64748B]">
              導入の流れやサービス内容を先に確認したい方へ
            </p>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link
                href="/process"
                className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-[10px] border border-[#0F766E] px-4 py-2 text-sm font-semibold text-[#0F766E] hover:bg-[#F0FDFA] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
              >
                導入の流れを見る
              </Link>
              <CtaButton href="/contact" className="!min-h-[44px] !text-sm">
                お問い合わせへ
              </CtaButton>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
