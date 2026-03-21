import { ShieldCheck } from "lucide-react";

export default function TsHubApproachMeasurementPrivacySection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <ShieldCheck className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              データと個人情報：取り扱いの考え方
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              取得は目的に限定し、保管期間・提供範囲は契約・運用で明確化します。サイト掲載の概要は、実運用に合わせて更新します。
            </p>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              点数や指標は対話の入口です。最終的に大事なのは、本人が納得して次の行動を選べることです。
            </p>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              走行に関する記録は個人情報・労務・安全管理の観点が絡みます。取得目的の限定、保管、削除、閲覧権限は、貴社ポリシーと整合する形で設計します。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
