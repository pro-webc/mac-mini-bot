export default function TrafficTipsPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-tips-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="traffic-tips-h1"
          className="text-left font-bold leading-[1.2] text-[#18181B]"
          style={{
            fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
          }}
        >
          朝礼ネタ・週次コラム
        </h1>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          1読30〜90秒想定。コピー可能な一文＋3つのチェック観点。
        </p>
        <p className="mt-3 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          煽りではなく、現場で再現できる行動に落とす。
        </p>
      </div>
    </section>
  );
}
