import Link from "next/link";

const items = [
  {
    title: "左折前の「最後の二秒」",
    date: "2025.03.17",
    read: "約1分",
    cat: "チェック観点",
    anchor: "featured_article",
  },
  {
    title: "雨の日は車間を最優先",
    date: "2025.03.10",
    read: "約1分",
    cat: "季節リスク",
    anchor: "archive_hint",
  },
  {
    title: "朝礼の一行質問（昨日の安全運転）",
    date: "2025.03.03",
    read: "約1分",
    cat: "意識づけ",
    anchor: "archive_hint",
  },
];

export default function TshTipsListSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="tips-list-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="tips-list-heading"
          className="scroll-mt-[calc(10vh+1rem)] text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          新着一覧
        </h2>
        <ul className="mt-10 flex flex-col gap-3">
          {items.map((it) => (
            <li key={it.title}>
              <Link
                href={`/tips#${it.anchor}`}
                className="flex flex-col gap-2 border border-[#e7e5e4] bg-[#fafaf9] p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="text-xs font-semibold text-[#0f766e]">
                    {it.cat}
                  </p>
                  <p className="mt-1 font-semibold text-[#1c1917]">{it.title}</p>
                </div>
                <div className="flex flex-wrap gap-3 text-sm text-[#57534e]">
                  <span>{it.date}</span>
                  <span>{it.read}</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
