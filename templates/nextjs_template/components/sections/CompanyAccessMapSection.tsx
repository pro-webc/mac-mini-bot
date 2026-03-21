import GoogleMapEmbed from "@/components/GoogleMapEmbed";

const MAP_EMBED =
  "https://maps.google.com/maps?q=%E5%A4%A7%E9%98%AA%E5%B8%82%E9%98%BF%E5%80%8D%E9%87%8E%E5%8C%BA%E4%B8%89%E6%98%8E%E7%94%BA2%E4%B8%81%E7%9B%AE16-5&hl=ja&z=17&output=embed";

export default function CompanyAccessMapSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="access-heading"
    >
      <h2 id="access-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        アクセス
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        大阪市阿倍野区三明町2丁目16-5。地図は Google Maps の埋め込みのみです（画像・プレースホルダは置いていません）。
      </p>
      <div className="mt-6">
        <GoogleMapEmbed
          title="株式会社ワン・ピース 所在地（大阪市阿倍野区三明町2丁目16-5）"
          embedUrl={MAP_EMBED}
        />
      </div>
    </section>
  );
}
