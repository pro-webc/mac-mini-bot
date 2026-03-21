import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TshTipsFeaturedSection() {
  return (
    <section
      id="featured_article"
      className="scroll-mt-[calc(10vh+1rem)] border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="featured-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="featured-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          今週の一口
        </h2>
        <article className="mt-10 border border-[#e7e5e4] bg-[#ffffff] p-6 md:p-8">
          <h3 className="text-xl font-semibold text-[#1c1917]">
            左折前の「最後の二秒」
          </h3>
          <p className="mt-2 text-sm text-[#57534e]">
            読了目安：45秒｜カテゴリ：チェック観点
          </p>
          <div className="mt-6">
            <ImagePlaceholder
              aspectClassName="aspect-[3/2]"
              description="朝礼の場を連想する明るいオフィス。司会台ではなく、資料を持った担当者の横位置シルエット。過度にフォーマルすぎない。"
            />
          </div>
          <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.7] text-[#1c1917]">
            <p>
              左折は、ウインカーを出したあとに急減速すると後続が非常に読みにくくなります。
            </p>
            <p>
              手順を「合図→確認→減速の配分」に分け、減速は直前に集中させないことが事故回避にも有効です。
            </p>
            <p>
              朝礼では、具体的な交差点名ではなく、チームの典型パターンを一つ挙げて話すと腹落ちしやすいです。
            </p>
          </div>
          <p className="mt-6 text-sm font-medium text-[#57534e]">
            現場の道路状況に合わせて言い換えて使ってください。
          </p>
        </article>
      </div>
    </section>
  );
}
