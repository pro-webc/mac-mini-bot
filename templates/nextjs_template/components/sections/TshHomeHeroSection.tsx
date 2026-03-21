import ImagePlaceholder from "@/components/ImagePlaceholder";
import CtaButton from "@/components/CtaButton";
import { BOOKING_URL } from "@/lib/bookingUrl";

export default function TshHomeHeroSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="home-hero-heading"
    >
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 md:grid-cols-2 md:items-center md:px-6 md:py-20">
        <div className="order-2 md:order-1">
          <p className="text-sm font-medium text-[#0f766e]">
            鹿児島市エリア｜法人向け
          </p>
          <h1
            id="home-hero-heading"
            className="mt-3 text-3xl font-bold leading-tight tracking-tight text-[#1c1917] md:text-4xl"
          >
            現場に戻るまでが、交通安全教育です。
          </h1>
          <p className="mt-5 max-w-prose text-left text-base font-normal leading-[1.7] text-[#1c1917]">
            机上の啓発で終わらせず、参加者同士の対話で「自分ごと」をつくり、一般道路での評価と振り返りで次の一手まで伴走します。
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
            <CtaButton href={BOOKING_URL}>相談予約を取る</CtaButton>
            <CtaButton
              href="/contact"
              className="!bg-[#ffffff] !text-[#0f766e] ring-2 ring-inset ring-[#0f766e] hover:!bg-[#f5f5f4] focus-visible:!outline-[#0f766e]"
            >
              お問い合わせする
            </CtaButton>
          </div>
        </div>
        <div className="order-1 md:order-2">
          <ImagePlaceholder
            aspectClassName="aspect-video"
            overlayText="鹿児島市エリア｜法人向けの伴走支援"
            description="鹿児島の穏やかな街路樹と明るい自然光。業務車が一台だけ写る程度で、事故や救助の暗示は避ける。人物は多様性配慮、落ち着いたビジネスカジュアル。全体トーンは柔らかいニュートラル＋ティールのアクセントが服の小物にだけ乗る程度。画角はワイド、余白多め。"
          />
        </div>
      </div>
    </section>
  );
}
