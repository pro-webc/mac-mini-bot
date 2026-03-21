import Link from "next/link";
import { FileText } from "lucide-react";

export default function TsHubContactPrivacyNoteSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <FileText className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              個人情報の取り扱い（概要）
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              取得した情報は、お問い合わせ対応およびご連絡の目的で利用します。法令に基づく場合を除き、本人の同意なく第三者へ提供しません。詳細は個人情報の取扱いページをご確認ください。
            </p>
            <Link
              href="/privacy"
              className="mt-4 inline-flex min-h-[44px] items-center text-sm font-semibold text-[#1D4ED8] hover:text-[#1E40AF] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            >
              個人情報の取扱いを読む
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
