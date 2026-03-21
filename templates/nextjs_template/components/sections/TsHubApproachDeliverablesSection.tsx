import { Package } from "lucide-react";

const items = [
  {
    title: "自分たちの言葉での優先課題",
    body: "社内で共有しやすい表現に整え、次の打ち手の議論に使える状態を目指します。",
  },
  {
    title: "次の一歩（小さく具体）",
    body: "翌週から試せる行動に落とし込み、運用に戻しやすくします。",
  },
];

export default function TsHubApproachDeliverablesSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Package className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
            研修後に持ち帰るもの（例）
          </h2>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {items.map(({ title, body }) => (
            <article
              key={title}
              className="border border-[#E4E4E7] bg-[#FAFAF9] p-5 sm:p-6"
            >
              <h3 className="text-left text-lg font-semibold text-[#18181B]">
                {title}
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {body}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
