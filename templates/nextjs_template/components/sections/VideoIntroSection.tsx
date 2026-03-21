export default function VideoIntroSection() {
  return (
    <section className="bg-[#F8FAFC] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          自己紹介動画（本掲載予定）
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          YouTube 等の埋め込みを想定しています。掲載可否・尺・顔出しの方針が確定し、URL が支給された段階で iframe を配置します。自動再生は行いません。
        </p>
        <div className="mt-8 overflow-hidden rounded-[20px] border-2 border-dashed border-[#CBD5E1] bg-[#FFFFFF]">
          <div className="flex aspect-video w-full flex-col items-center justify-center gap-2 px-4 py-10">
            <p className="text-center text-sm font-medium text-[#0F172A]">
              動画 iframe プレース（URL 確定後に設定）
            </p>
            <p className="max-w-lg text-center text-xs leading-relaxed text-[#475569]">
              iframe には loading=&quot;lazy&quot; での遅延読み込みを前提に実装します。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
