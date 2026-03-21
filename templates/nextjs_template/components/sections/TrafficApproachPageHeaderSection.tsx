export default function TrafficApproachPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-approach-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="traffic-approach-h1"
          className="text-left font-bold leading-[1.2] text-[#18181B]"
          style={{
            fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
          }}
        >
          進行と評価の仕組み
        </h1>
        <p className="mt-6 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          「警察の話を聞いただけ」では再現性が出にくい論点を踏まえた設計。
        </p>
      </div>
    </section>
  );
}
