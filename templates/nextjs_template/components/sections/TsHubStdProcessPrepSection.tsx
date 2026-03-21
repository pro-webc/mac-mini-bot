export default function TsHubStdProcessPrepSection() {
  const bullets = [
    "対象人数と職種の概算",
    "車両運用の概要（配車、定期点検、報告の流れなど）",
    "過去に実施した教育があれば資料（任意）",
    "社内の窓口担当者名（連絡用）",
  ];
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="prep-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="prep-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          事前にお願いしたいこと
        </h2>
        <ul className="mt-8 flex max-w-prose flex-col gap-3">
          {bullets.map((b) => (
            <li
              key={b}
              className="border-l-4 border-[#14B8A6] pl-4 text-left text-base leading-[1.7] text-[#0F172A]"
            >
              {b}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
