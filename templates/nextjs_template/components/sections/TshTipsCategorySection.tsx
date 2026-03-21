import Link from "next/link";

const cats = [
  {
    title: "意識づけ",
    desc: "習慣化のきっかけ",
    id: "cat-awareness",
  },
  {
    title: "季節リスク",
    desc: "天候・時間帯の注意",
    id: "cat-season",
  },
  {
    title: "チェック観点",
    desc: "点検と確認の観点",
    id: "cat-check",
  },
];

export default function TshTipsCategorySection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="tips-cat-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="tips-cat-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          カテゴリから読む
        </h2>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {cats.map((c) => (
            <Link
              key={c.id}
              id={c.id}
              href={`/tips#${c.id}`}
              className="flex flex-col justify-between border border-[#e7e5e4] bg-[#ffffff] p-5 transition-colors hover:border-[#0f766e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            >
              <div>
                <h3 className="text-lg font-semibold text-[#1c1917]">
                  {c.title}
                </h3>
                <p className="mt-2 text-sm text-[#57534e]">{c.desc}</p>
              </div>
              <span className="mt-4 text-sm font-semibold text-[#0f766e]">
                該当の記事へ
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
