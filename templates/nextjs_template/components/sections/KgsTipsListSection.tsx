import Link from "next/link";

const articles = [
  {
    slug: "weekly-2025-03-21-01",
    published: "2025-03-21",
    title: "右折待ちの「ながら」を減らす：一言チェック",
    lead: "信号待ちは注意が散漫になりやすい。短い確認でリスクを下げる。",
    morning_line:
      "今日は右折前に、ミラーと死角を“名前を言う”つもりで確認しよう。",
    bullets: [
      "ハンドルに触れる前に、確認順序を決める",
      "後続が迫る場面では、無理な寄りをしない",
      "共有：うまくいった確認順をチームで交換",
    ],
  },
  {
    slug: "weekly-2025-03-14-02",
    published: "2025-03-14",
    title: "出庫前30秒：白ナンバー現場の定番ミス再点検",
    lead: "忙しい朝ほど、固定化した確認が効く。",
    morning_line: "出庫前に「タイヤ・ライト・荷物の固定」を口に出して確認。",
    bullets: [
      "荷台・積載の固定は音が変わるサインも見逃さない",
      "ドア周りの挟み込みは再発しやすい",
      "写真共有は個人情報に注意（ナンバー・顔）",
    ],
  },
  {
    slug: "weekly-2025-03-07-03",
    published: "2025-03-07",
    title: "「注意しただけ」で終わらせない振り返りの型",
    lead: "指摘は事実と影響に分けて伝えると現場が受け取りやすい。",
    morning_line:
      "ヒヤリは「何が起きたか」「次は何を変えるか」の2行で共有。",
    bullets: [
      "人格ではなく行動にフォーカス",
      "再発防止は一人の努力だけに依存しない",
      "次回研修の論点に昇格させる基準を決める",
    ],
  },
];

export default function KgsTipsListSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-tips-list-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-tips-list-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          最新記事一覧（デモ用に複数本）
        </h2>
        <ul className="mt-10 flex flex-col gap-8">
          {articles.map((a) => (
            <li
              key={a.slug}
              id={a.slug}
              className="border border-[#E4E4E7] bg-[#FAFAF9] p-6"
            >
              <h3 className="text-left text-xl font-bold text-[#18181B]">
                {a.title}
              </h3>
              <p className="mt-2 text-left text-sm text-[#52525B]">
                公開日：{a.published}
              </p>
              <p className="mt-4 text-left text-base leading-relaxed text-[#18181B]">
                {a.lead}
              </p>
              <p className="mt-4 border border-[#E4E4E7] bg-[#FFFFFF] p-4 text-left text-base font-medium text-[#18181B]">
                朝礼で読む一文：{a.morning_line}
              </p>
              <ul className="mt-4 space-y-2 text-left text-sm leading-relaxed text-[#18181B]">
                {a.bullets.map((b) => (
                  <li key={b}>・{b}</li>
                ))}
              </ul>
              <div className="mt-6 flex flex-wrap gap-4">
                <Link
                  href="/services"
                  className="inline-flex min-h-[44px] min-w-[44px] items-center text-sm font-semibold text-[#1D4ED8] underline-offset-4 hover:text-[#1E40AF] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
                >
                  講習・支援内容を見る
                </Link>
                <Link
                  href="/measurement"
                  className="inline-flex min-h-[44px] min-w-[44px] items-center text-sm font-semibold text-[#1D4ED8] underline-offset-4 hover:text-[#1E40AF] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
                >
                  見える化・評価を見る
                </Link>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
