import Link from "next/link";
import { Link2 } from "lucide-react";

export default function CompanyGroupContextSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="group-context-heading"
    >
      <h2
        id="group-context-heading"
        className="inline-flex items-center gap-2 text-xl font-bold text-white md:text-2xl"
      >
        <Link2 className="h-7 w-7 text-[#caeb25]" aria-hidden />
        親会社グループとの関係
      </h2>
      <div className="mt-4 space-y-4 text-left text-base leading-relaxed text-[#E0E7FF]">
        <p>
          株式会社タスク・フォースは関連サイト（
          <Link
            href="https://task888.com/"
            className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
            rel="noopener noreferrer"
            target="_blank"
          >
            task888.com
          </Link>
          ／
          <Link
            href="https://task888-recruit.com/"
            className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
            rel="noopener noreferrer"
            target="_blank"
          >
            task888-recruit.com
          </Link>
          ）で情報を発信しています。資本関係・グループ表記・素材利用範囲は、公開前に整備します。
        </p>
        <p className="text-sm text-[#BFDBFE]">
          世界観の整合は許諾範囲確定後に反映します。デモ掲載はプレースホルダーと撮影意図の説明で構成しています。
        </p>
      </div>
    </section>
  );
}
