export default function TrafficServicesPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-services-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="traffic-services-h1"
          className="text-left font-bold leading-[1.2] text-[#18181B]"
          style={{
            fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
          }}
        >
          サービス・研修内容
        </h1>
        <p className="mt-6 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          企業向け：交通安全教育・研修。安全運転管理者／運行管理担当を当面の主ターゲットに設定。
        </p>
      </div>
    </section>
  );
}
