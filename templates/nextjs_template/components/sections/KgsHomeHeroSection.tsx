import Link from "next/link";
import { ArrowRight, MessageCircle, Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

const secondaryOutlineClass =
  "inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#1D4ED8] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:border-[#1E40AF] hover:bg-[#F4F4F5] active:bg-[#E4E4E7] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] motion-safe:transition-colors";

const tertiaryLinkClass =
  "inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 text-base font-semibold text-[#1D4ED8] underline-offset-4 hover:text-[#1E40AF] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]";

export default function KgsHomeHeroSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] pb-12 pt-6 md:pb-20 md:pt-10"
      aria-labelledby="kgs-home-hero-h1"
    >
      <div className="mx-auto flex max-w-6xl flex-col items-center px-4 text-center md:px-6">
        <h1
          id="kgs-home-hero-h1"
          className="max-w-4xl text-balance text-3xl font-bold leading-tight tracking-tight text-[#18181B] md:text-4xl"
        >
          現場が変わるのは「注意」だけじゃない。対話と見える化から。
        </h1>
        <div className="mt-8 flex w-full max-w-md flex-col gap-3 sm:max-w-none sm:flex-row sm:flex-wrap sm:justify-center">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            無料で相談予約する
          </CtaButton>
          <Link
            href="/services"
            className={`${secondaryOutlineClass} w-full sm:w-auto`}
          >
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            支援内容を見る
          </Link>
        </div>
        <p className="mt-8 max-w-prose text-left text-base leading-relaxed text-[#18181B] md:text-center">
          鹿児島の企業向けに、コーチング型の交通安全教育と、走行を前提とした技能評価の支援を行っています。担当者の毎週の「話の種」になる更新も。
        </p>
        <p className="mt-3 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-center">
          ※正式な事業者表記・連絡先は確定後に更新します。
        </p>
        <Link href="/tips" className={`${tertiaryLinkClass} mt-6`}>
          <MessageCircle className="h-5 w-5 shrink-0" aria-hidden />
          一口アドバイスを読む
        </Link>
      </div>
      <div className="mx-auto mt-10 max-w-6xl border-y border-[#E4E4E7] bg-[#FAFAF9] px-4 py-4 md:px-6">
        <p className="mx-auto max-w-4xl text-left text-sm leading-relaxed text-[#52525B]">
          主商圏は鹿児島市周辺の法人です。一人運営のため、同時多発の大型案件は想定していません。全国規模の大量集客も目的としていません（期待値のすり合わせを重視します）。
        </p>
      </div>
    </section>
  );
}
