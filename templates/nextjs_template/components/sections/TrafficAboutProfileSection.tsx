import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TrafficAboutProfileSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-profile-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-profile-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          プロフィール（公開情報は確定待ち）
        </h2>
        <ul className="mt-6 max-w-prose list-disc space-y-2 pl-5 text-left text-base leading-relaxed text-[#18181B]">
          <li>代表／資格／活動エリアは確定後に表またはリストで掲載</li>
          <li>写真は許諾取得後に差し替え（現時点はプレースホルダ）</li>
        </ul>
        <div className="mt-8 max-w-md">
          <ImagePlaceholder
            description="代表プロフィール用の落ち着いたトーンのポートレート（許諾取得後に差し替え）"
            aspectClassName="aspect-[4/5]"
            overlayText="（公開用写真の意図：信頼感・現場伴走の印象）"
          />
        </div>
      </div>
    </section>
  );
}
