import { UserCog, Car, Shield } from "lucide-react";

export default function TsRolesResponsibilitiesSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="roles-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="roles-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          企業側の準備と役割
        </h2>
        <ul className="mt-8 space-y-4">
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <UserCog className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              安全運転管理者・運行管理者など、窓口担当の設定
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <Car className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              車両・コース設定に関する社内調整の協力
            </p>
          </li>
          <li className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5">
            <Shield className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
              個人情報・映像等の取り扱いは確定次第で表記更新
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
