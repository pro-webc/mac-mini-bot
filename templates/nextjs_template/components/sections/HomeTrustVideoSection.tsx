import { Video } from "lucide-react";

export default function HomeTrustVideoSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="trust-video-heading"
    >
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="max-w-xl">
          <h2
            id="trust-video-heading"
            className="inline-flex items-center gap-2 text-xl font-bold text-[#0F172A] md:text-2xl"
          >
            <Video className="h-6 w-6 text-[#0284C7]" aria-hidden />
            自己紹介動画（掲載準備中）
          </h2>
          <p className="mt-3 text-left text-base leading-relaxed text-[#475569]">
            「誰が来るのか」を動画でお届けする予定です。収録の尺（目安：1〜3分）や掲載可否が確定次第、YouTube
            等の埋め込みを設置します。未掲載の間は、お問い合わせでご希望を伺いながら進めます。
          </p>
        </div>
        <p className="rounded-none border border-dashed border-[#CBD5E1] bg-[#F8FAFC] p-4 text-sm leading-relaxed text-[#64748B] md:max-w-sm">
          収録・編集の方針：作業服の清潔感、声のトーン、現場での挨拶の流れが伝わる構成を想定。字幕の有無は公開前にすり合わせます。
        </p>
      </div>
      <div
        className="mt-6 flex aspect-video w-full items-center justify-center border-2 border-dashed border-[#CBD5E1] bg-[#F1F5F9]"
        role="status"
        aria-live="polite"
      >
        <p className="px-4 text-center text-sm font-medium text-[#475569]">
          動画URL確定後に、この枠にプレーヤーを埋め込みます（外部動画の読み込みは遅延表示を検討します）。
        </p>
      </div>
    </section>
  );
}
