import GoogleMapEmbed from "@/components/GoogleMapEmbed";

/** 住所未確定のため鹿児島市中央部付近を暫定表示。住所・ピンは確定後に更新。 */
const KAGOSHIMA_CITY_EMBED =
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&hl=ja&z=12&output=embed";

export default function TrafficContactMapSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-contact-map-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-contact-map-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          拠点（鹿児島市）
        </h2>
        <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B]">
          Google Maps埋め込みのみ（画像プレースホルダ禁止）。詳細住所確定後にピンを正確化します。
        </p>
        <div className="mt-8 max-w-4xl rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-1">
          <GoogleMapEmbed
            title="鹿児島市（暫定表示）"
            embedUrl={KAGOSHIMA_CITY_EMBED}
          />
        </div>
      </div>
    </section>
  );
}
