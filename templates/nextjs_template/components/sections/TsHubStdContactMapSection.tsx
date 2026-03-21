import GoogleMapEmbed from "@/components/GoogleMapEmbed";

const KAGOSHIMA_EMBED =
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&z=12&hl=ja&ie=UTF8&output=embed";

export default function TsHubStdContactMapSection() {
  return (
    <section
      className="border border-[#E2E8F0] bg-[#FFFFFF] p-4 md:p-6"
      aria-labelledby="map-heading"
    >
      <h2
        id="map-heading"
        className="text-lg font-semibold text-[#0F172A]"
      >
        対応エリアの目安（鹿児島市）
      </h2>
      <p className="mt-2 text-sm text-[#64748B]">
        正確な住所が確定した際は、埋め込みを差し替えます。対応範囲は事前にすり合わせます。
      </p>
      <div className="mt-4">
        <GoogleMapEmbed
          embedUrl={KAGOSHIMA_EMBED}
          title="鹿児島市周辺の地図"
        />
      </div>
    </section>
  );
}
