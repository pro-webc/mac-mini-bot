import GoogleMapEmbed from "@/components/GoogleMapEmbed";

/** 住所確定までは鹿児島市周辺の暫定表示。ピンは確定後に更新。 */
const KAGOSHIMA_CITY_EMBED =
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&z=12&hl=ja&output=embed";

export default function KgsContactMapSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-contact-map-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-contact-map-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          対応エリア（地図）
        </h2>
        <ul className="mt-6 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          <li>
            住所確定までは鹿児島市を中心とした暫定表示でも可（ピン位置は確定後に更新）
          </li>
          <li>対応エリアのイラスト地図は使わない</li>
        </ul>
        <div className="mt-8 min-h-[min(70vh,560px)] w-full md:aspect-auto md:min-h-[420px]">
          <GoogleMapEmbed
            title="鹿児島市周辺（暫定表示）"
            embedUrl={KAGOSHIMA_CITY_EMBED}
          />
        </div>
      </div>
    </section>
  );
}
