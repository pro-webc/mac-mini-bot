import Link from "next/link";
import { ExternalLink } from "lucide-react";

export default function CompanyRecruitSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="company-recruit-heading"
    >
      <h2
        id="company-recruit-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        採用について
      </h2>
      <p className="mt-4 text-left text-base leading-relaxed text-[#E0E7FF]">
        採用は親会社の採用サイトを主軸にご案内します。応募要件や募集職種の最新情報は、以下のサイトでご確認ください（外部リンクは許諾確認後の運用を想定）。
      </p>
      <div className="mt-6">
        <Link
          href="https://task888-recruit.com/"
          rel="noopener noreferrer"
          target="_blank"
          className="inline-flex min-h-[48px] min-w-[44px] items-center gap-2 rounded-full border-2 border-[#caeb25] bg-[#2563eb] px-6 py-3 text-base font-semibold text-[#caeb25] transition-colors hover:bg-[#1e40af] hover:text-white active:bg-[#1e3a8a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          親会社採用サイトを見る
          <ExternalLink className="h-5 w-5" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
