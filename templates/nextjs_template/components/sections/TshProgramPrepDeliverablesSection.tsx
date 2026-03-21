export default function TshProgramPrepDeliverablesSection() {
  const prep = [
    "対象者範囲、車両条件、実施ルートの安全確認",
    "個人情報・データ取り扱いの社内確認担当の指定",
    "運行記録やヒヤリハット事例があれば共有（任意）",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="prep-deliv-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="prep-deliv-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          事前準備（例）
        </h2>
        <ul className="mt-8 flex flex-col gap-3">
          {prep.map((t) => (
            <li
              key={t}
              className="border border-[#e7e5e4] bg-[#fafaf9] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              {t}
            </li>
          ))}
        </ul>
        <h3 className="mt-12 text-xl font-semibold text-[#1c1917]">
          成果物（一般）
        </h3>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          協議の結果として、振り返りシート、簡易レポート、管理者向けFAQ草案などをご提案することがあります。内容は個別契約に基づきます。
        </p>
      </div>
    </section>
  );
}
