import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function RecruitHeroSection() {
  return (
    <section
      className="overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1e40af] p-6 md:p-10"
      aria-labelledby="recruit-hero-heading"
    >
      <div className="flex flex-col gap-8 lg:flex-row lg:items-center">
        <div className="flex-1">
          <p className="text-sm font-semibold text-[#caeb25]">採用情報</p>
          <h1
            id="recruit-hero-heading"
            className="mt-2 text-3xl font-bold tracking-tight text-white md:text-4xl"
          >
            現場が、次のステージになる。
          </h1>
          <p className="mt-4 text-xl font-semibold text-[#BFDBFE]">新しい3Kへ。</p>
          <p className="mt-4 text-left text-base leading-relaxed text-[#E0E7FF]">
            かっこいい装備と手に職。稼ぎがいい土台を、チームで作る。
          </p>
        </div>
        <div className="w-full flex-1">
          <ImagePlaceholder
            aspectClassName="aspect-video"
            description="掲載予定：整然とした安全装備・チームコミュニケーションが伝わる現場イメージ。クールで引き締まったトーン。実素材は public/images/generated/ へ差し替え。"
            overlayText="かっこいい現場・新しい3Kのビジュアル（差し替え想定）"
          />
        </div>
      </div>
    </section>
  );
}
