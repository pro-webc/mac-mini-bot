import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TsHubStdAboutProfileSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="profile-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="profile-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          プロフィール（文案の型）
        </h2>
        <div className="mt-10 grid gap-10 md:grid-cols-2 md:items-start">
          <ImagePlaceholder
            aspectClassName="aspect-[3/4]"
            description="講師ポートレート枠：自然光の室内。表情は穏やか、視線はカメラ寄り。背景は単色〜軽いボケ。服装はビジネスカジュアル。顔は後日差し替え前提でプレースホルダ。"
            overlayText="講師写真（差し替え予定）"
          />
          <div className="max-w-prose">
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              交通教育に携わり、法人向けの講習・伴走に取り組んできました。現場の対話と、評価の見える化を組み合わせて、社内で続く仕組みづくりを支援します。
            </p>
            <p className="mt-4 text-left text-base leading-[1.7] text-[#0F172A]">
              肩書・経歴の詳細は、公開情報として確定次第、追記します。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
