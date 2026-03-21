import { AlertCircle } from "lucide-react";

const items = [
  "朝礼で毎回、新しい交通安全ネタを考えるのが大変",
  "啓発が一口メッセージに留まり、現場の行動が変わりにくい",
  "自社運用に閉じがちで、改善の型が見えにくい",
  "「話を聞いた」だけでは、改善の実感が出にくい",
];

export default function TsHubPainSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="pain-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="pain-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          こんな負担、ありませんか
        </h2>
        <ul className="mt-8 space-y-4">
          {items.map((text) => (
            <li
              key={text}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4 md:p-5"
            >
              <AlertCircle
                className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]"
                aria-hidden
              />
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                {text}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
