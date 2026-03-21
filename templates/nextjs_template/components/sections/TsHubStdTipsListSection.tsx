import Link from "next/link";

const articles = [
  {
    slug: "weekly-check-01",
    title: "出発前30秒：今日の「見る順番」を固定する",
    summary:
      "ミラーと死角、歩行者の優先を、最初の一台で揃えるとブレが減ります。",
    date: "2025.03.01",
  },
  {
    slug: "handover-one-liner",
    title: "配車交代の一言：「道路は変わった」前提で渡す",
    summary: "前便の慣れを引きずらないための、短い引き継ぎテンプレ。",
    date: "2025.03.08",
  },
  {
    slug: "meeting-starter",
    title: "安全会議の冒頭1分：事実→仮説→次の一回",
    summary: "感想で終わらせず、次の運行に接続する進行の型。",
    date: "2025.03.15",
  },
];

export default function TsHubStdTipsListSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="tips-list-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="tips-list-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          最新の記事
        </h2>
        <p className="mt-4 text-sm text-[#64748B]">
          運用開始後は、掲載日順で並べ替えます。
        </p>
        <ul className="mt-10 flex flex-col gap-6">
          {articles.map((a) => (
            <li key={a.slug}>
              <article className="flex h-full flex-col justify-between rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6">
                <div>
                  <time
                    dateTime={a.date.replace(/\./g, "-")}
                    className="text-sm text-[#64748B]"
                  >
                    掲載日 {a.date}
                  </time>
                  <h3 className="mt-2 text-xl font-semibold text-[#0F172A]">
                    <Link
                      href={`/tips/${a.slug}`}
                      className="hover:text-[#0F766E] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
                    >
                      {a.title}
                    </Link>
                  </h3>
                  <p className="mt-3 max-w-prose text-left text-base text-[#64748B]">
                    {a.summary}
                  </p>
                </div>
                <div className="mt-6">
                  <Link
                    href={`/tips/${a.slug}`}
                    className="inline-flex min-h-[44px] min-w-[44px] items-center text-sm font-semibold text-[#0F766E] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
                  >
                    記事を読む
                  </Link>
                </div>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
