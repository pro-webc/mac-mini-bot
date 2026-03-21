import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TsProfileHanyuSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="profile-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="profile-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          担当：羽生（ハブ）
        </h2>
        <div className="mt-8 grid gap-8 md:grid-cols-[minmax(0,280px)_1fr] md:items-start">
          <ImagePlaceholder
            description="担当者紹介用の顔写真（柔らかい自然光・信頼感のある構図）。提供後に差し替え。"
            aspectClassName="aspect-[4/5] max-w-[280px]"
            className="mx-auto w-full md:mx-0"
          />
          <ul className="space-y-4">
            <li className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                交通関連業務に長く従事し、現場の課題感を材料に設計する
              </p>
            </li>
            <li className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                事故現場経験や企業担当者の声を、講義の文脈づくりに活かす
              </p>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
