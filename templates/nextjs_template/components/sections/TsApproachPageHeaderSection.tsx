export default function TsApproachPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="approach-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="approach-h1"
          className="text-left text-2xl font-bold text-[#18181B] md:text-3xl"
        >
          進め方：対話・可視化・評価
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>一方通行の説教に寄せず、現場が動く言葉に落とします。</p>
          <p>
            担当者が後から説明しやすい「構造」をサイト上に固定化します。
          </p>
        </div>
      </div>
    </section>
  );
}
