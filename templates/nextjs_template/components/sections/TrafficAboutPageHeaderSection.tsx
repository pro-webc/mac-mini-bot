export default function TrafficAboutPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-about-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="traffic-about-h1"
          className="text-left font-bold leading-[1.2] text-[#18181B]"
          style={{
            fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
          }}
        >
          想いと背景
        </h1>
        <p className="mt-6 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          約30年に近い交通関連の実務、現場・事故対応の経験を根拠に論点を整理。
        </p>
      </div>
    </section>
  );
}
