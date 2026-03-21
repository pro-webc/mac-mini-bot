export default function TsContactMapSection() {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="map-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="map-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          所在地（確定後に地図埋め込み）
        </h2>
        <div className="mt-8 space-y-4 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-6">
          <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            住所確定後、Google Maps iframeを配置
          </p>
          <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            それまでは「準備中」＋対応エリア文言のみ
          </p>
          <p className="text-left text-base font-medium text-[#0F766E]">
            対応エリア：鹿児島市周辺（詳細は相談）
          </p>
          <p className="text-left text-sm text-[#52525B]">
            地図は後日設置します。マップ表示エリアには画像やプレースホルダを置きません。
          </p>
        </div>
      </div>
    </section>
  );
}
