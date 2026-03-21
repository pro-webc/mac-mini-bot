import { Briefcase } from "lucide-react";

export default function TsHubServicesManagersSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="border border-[#E4E4E7] bg-[#FFFFFF] p-6 sm:p-8">
          <div className="flex items-start gap-3">
            <Briefcase className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
            <div>
              <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
                安全運転管理者・運行管理担当者向け
              </h2>
              <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                制度運用の説明に閉じこもらず、現場の行動変容につながる言葉と型を一緒に作ります。社内稟議や関係部署への説明にも使える資料の骨子づくりも支援します。
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
