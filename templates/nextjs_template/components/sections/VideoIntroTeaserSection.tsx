export default function VideoIntroTeaserSection() {
  return (
    <section className="bg-[#FFFFFF] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          自己紹介動画（準備中）
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          代表・現場担当の雰囲気が伝わる短い動画を掲載予定です。尺・収録方法・顔出しの可否はクライアント様にて確定後、埋め込みを設定します。
        </p>
        <div className="mt-8 overflow-hidden rounded-[20px] border-2 border-dashed border-[#CBD5E1] bg-[#F8FAFC]">
          <div className="flex aspect-video w-full flex-col items-center justify-center gap-3 px-4 py-8">
            <p className="text-center text-sm font-medium text-[#0F172A]">
              動画埋め込みエリア（iframe は URL 確定後に配置）
            </p>
            <p className="max-w-lg text-center text-sm leading-relaxed text-[#475569]">
              自動再生・音声オンにはしません。YouTube 等の URL が決まり次第、本枠に読み込みます。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
