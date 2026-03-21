import Link from "next/link";
import { Phone } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-[#E0F2FE] via-[#F8FAFC] to-[#BAE6FD] px-4 pb-16 pt-28 md:px-6 md:pb-24 md:pt-32">
      <div
        className="pointer-events-none absolute -right-16 top-10 h-48 w-48 rounded-[32px] border-2 border-[#0EA5E9]/40 bg-[#0EA5E9]/10 md:h-64 md:w-64"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute bottom-8 left-4 h-32 w-32 rounded-full border-2 border-[#0369A1]/30 md:left-10 md:h-40 md:w-40"
        aria-hidden
      />
      <div className="relative mx-auto max-w-6xl">
        <p className="text-sm font-semibold text-[#0369A1]">
          訪問型の施工サービス
        </p>
        <h1 className="mt-3 max-w-2xl text-3xl font-bold tracking-tight text-[#0F172A] md:text-4xl">
          おうちに入る前から、ちゃんと顔が見える関係でありたい。
        </h1>
        <p className="mt-6 max-w-xl text-left text-base leading-relaxed text-[#475569]">
          初めてのご依頼でも緊張しすぎないよう、流れや連絡方法をわかりやすくご案内します。詳しい業種ラベルや範囲は確定次第、サイト上でも補足していきます。
        </p>
        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
          <CtaButton href="/contact">お問い合わせ・見積の相談</CtaButton>
          <a
            href="tel:0471227322"
            className="inline-flex min-h-[48px] items-center justify-center gap-2 rounded-[14px] border-2 border-[#0284C7] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0284C7] transition-colors hover:border-[#0369A1] hover:bg-[#F0F9FF] hover:text-[#0369A1] active:border-[#075985] active:text-[#075985] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
          >
            <Phone className="h-5 w-5 shrink-0" aria-hidden />
            0471-22-7322（暫定）
          </a>
        </div>
        <p className="mt-4 text-left text-xs text-[#475569]">
          電話番号・受付時間は確定情報に合わせて更新予定です。{" "}
          <Link
            href="/company"
            className="font-medium text-[#0369A1] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
          >
            会社概要
          </Link>
          もあわせてご覧ください。
        </p>
      </div>
    </section>
  );
}
