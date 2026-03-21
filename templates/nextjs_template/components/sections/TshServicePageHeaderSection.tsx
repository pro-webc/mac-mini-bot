export default function TshServicePageHeaderSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="service-page-h1"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h1
          id="service-page-h1"
          className="text-3xl font-bold text-[#1c1917] md:text-4xl"
        >
          サービス概要
        </h1>
        <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          このページでは、TS-hubの支援が「誰の、どんな詰まり」に効きやすいかを先に明確にし、机上講義との違い、コーチング型の進行、評価の位置づけまでをひと通り説明します。
        </p>
      </div>
    </section>
  );
}
