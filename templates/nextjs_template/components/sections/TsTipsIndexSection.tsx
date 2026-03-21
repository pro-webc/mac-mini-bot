const posts = [
  "【デモ】出庫前の30秒：今日だけ確認する1項目を決める",
  "【デモ】横断歩道手前：止まり方の説明を統一するコツ",
  "【デモ】疲労気味の日：本人が自分で言える一言",
];

export default function TsTipsIndexSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="tips-index-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="tips-index-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          最新記事
        </h2>
        <ul className="mt-8 space-y-3">
          {posts.map((title) => (
            <li key={title}>
              <div className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
                <h3 className="text-left text-base font-semibold text-[#18181B]">
                  {title}
                </h3>
                <p className="mt-2 text-left text-sm text-[#52525B]">
                  掲載開始後、本文エリアに差し替えます。
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
