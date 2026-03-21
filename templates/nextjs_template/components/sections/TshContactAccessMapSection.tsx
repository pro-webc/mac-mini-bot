import GoogleMapEmbed from "@/components/GoogleMapEmbed";

const KAGOSHIMA_EMBED =
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&z=12&hl=ja&ie=UTF8&output=embed";

export default function TshContactAccessMapSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="access-map-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="access-map-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          所在地・アクセス
        </h2>
        <p className="mt-4 text-sm text-[#57534e]">
          〒890-XXXX 鹿児島県鹿児島市（確定後に更新）
        </p>
        <p className="mt-1 text-sm text-[#57534e]">
          Tel（確定後に更新）／ info@example.com（確定後に更新）
        </p>
        <p className="mt-2 text-sm text-[#57534e]">
          正確な所在地が確定したら、地図の埋め込みを差し替えます。
        </p>
        <div className="mt-6">
          <GoogleMapEmbed
            embedUrl={KAGOSHIMA_EMBED}
            title="鹿児島市周辺の地図"
          />
        </div>
      </div>
    </section>
  );
}
