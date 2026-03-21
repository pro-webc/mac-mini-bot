import ImagePlaceholder from "@/components/ImagePlaceholder";

const samples = [
  {
    title: "今日の一文：確認ミラーの意味を言語化する",
    body: "「見る」ではなく「何が見えたら次に何をするか」まで言えるかを一人ずつ短く共有してください。",
  },
  {
    title: "今日の一文：急がない約束を、チームで作る",
    body: "遅刻不安が速度に出やすい日を想定し、現場ルールを一言で合意して終わりましょう。",
  },
  {
    title: "今日の一文：疲労の自己点検",
    body: "眠気のサインを三つ挙げ、気づいたら止まれる報告ラインを確認してください。",
  },
];

export default function TsHubTipsIndexSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          最近のTips
        </h2>
        <div className="mt-10 grid items-start gap-10 lg:grid-cols-2">
          <div className="space-y-4">
            {samples.map(({ title, body }) => (
              <article
                key={title}
                className="border border-[#E4E4E7] bg-[#FAFAF9] p-5 sm:p-6"
              >
                <h3 className="text-left text-lg font-semibold text-[#18181B]">
                  {title}
                </h3>
                <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                  {body}
                </p>
              </article>
            ))}
          </div>
          <div>
            <ImagePlaceholder
              description="朝礼のイメージ：明るい会議室で担当者が短いメモカードを手にしている。顔は識別しにくい角度。背景はシンプル。"
              aspectClassName="aspect-[3/2]"
              overlayText="週次の短いネタとして、そのまま使える分量"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
