import { MapPinned, UserCircle2 } from "lucide-react";

export default function TsHubStdAboutScopeSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="scope-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="scope-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          対応範囲・進め方
        </h2>
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-6">
            <MapPinned className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              対応エリアは鹿児島市を中心に周辺地域。詳細は事前に確認します。
            </p>
          </div>
          <div className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-6">
            <UserCircle2 className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              窓口は一本化し、要件の取り違えを減らす進行を心がけます。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
