import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function KgsAboutProfileSection() {
  const items = [
    "約30年にわたる交通安全関連の実務経験（現場・事故対応の文脈）※詳細肩書は要確認",
    "コーチング型進行と見える化を組み合わせる理由を短く記載",
    "顔写真：許諾・品質確定後に掲載。未確定はシルエット＋説明文で代替可",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-about-profile-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-about-profile-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          プロフィール（公開情報は確定後に反映）
        </h2>
        <div className="mt-10 grid gap-10 md:grid-cols-[minmax(0,280px)_1fr] md:items-start">
          <ImagePlaceholder
            aspectClassName="aspect-[3/4]"
            description="掲載予定：顔写真（許諾・品質確定後）。現時点はプレースホルダ。背景は落ち着いたニュートラル、視線は正面〜やや横、現場の安全帽・社用車は案件方針に合わせて調整。"
            overlayText="（デモ）代表／講師の顔写真エリア"
          />
          <ul className="max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
            {items.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
