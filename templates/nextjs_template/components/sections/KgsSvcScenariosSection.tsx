export default function KgsSvcScenariosSection() {
  const items = [
    "朝礼・安全ミーティングのネタ提供と運用定着",
    "新任管理者への引き継ぎ資料としての利用",
    "事故・ヒヤリハット後の再発防止学習の組み立て",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="kgs-svc-scenarios-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-svc-scenarios-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          よくあるシーン別の切り口
        </h2>
        <ul className="mt-8 grid gap-4 md:grid-cols-3">
          {items.map((t) => (
            <li
              key={t}
              className="border border-[#E4E4E7] bg-[#FFFFFF] p-5 text-left text-base leading-relaxed text-[#18181B]"
            >
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
