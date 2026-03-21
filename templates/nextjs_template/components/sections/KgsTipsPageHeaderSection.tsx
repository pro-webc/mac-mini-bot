export default function KgsTipsPageHeaderSection() {
  const items = [
    "安全運転管理者が朝礼でそのまま使える短い「問いかけ」と「チェック観点」",
    "更新頻度・分量は制作後の月次修正枠と相談して現実的に調整",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-tips-header-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="kgs-tips-header-h1"
          className="text-left text-3xl font-bold tracking-tight text-[#18181B] md:text-4xl"
        >
          一口アドバイス（週次更新）
        </h1>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
