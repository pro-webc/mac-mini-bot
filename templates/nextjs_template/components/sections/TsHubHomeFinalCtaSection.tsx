import CtaButton from "@/components/CtaButton";
import Link from "next/link";

export default function TsHubHomeFinalCtaSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-6 sm:p-10 md:p-12">
          <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
            まずは15分のすり合わせからでも構いません
          </h2>
          <p className="mt-4 max-w-prose text-left text-base leading-[1.75] text-[#52525B]">
            課題感、対象者、希望時期が固まっていなくても問題ありません。現状をお聞きし、次に取るべき打ち手を一緒に切り分けます。
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
            <CtaButton href="/contact">相談フォームを開く</CtaButton>
            <Link
              href="/approach"
              className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center rounded-[12px] border-2 border-[#1D4ED8] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:bg-[#EFF6FF] active:bg-[#DBEAFE] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            >
              進め方を読む
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
