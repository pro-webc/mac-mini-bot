import { AlertCircle } from "lucide-react";

const items = [
  "各社ごとに安全啓発の型がバラバラで、良い打ち手が社内に残りにくい",
  "朝礼や短時間の場で、毎回のネタ出しが負担になっている",
  "運転の課題が感覚論になりがちで、説明・共有が難しい",
  "外部研修後に「何が変わったか」を言語化しづらい",
];

export default function TrafficHomePainSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-pain-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <AlertCircle
            className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]"
            aria-hidden
          />
          <div className="min-w-0 flex-1">
            <h2
              id="traffic-pain-heading"
              className="text-left font-semibold leading-[1.35] text-[#18181B]"
              style={{
                fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
                fontWeight: 650,
              }}
            >
              安全担当者の現場で、よくある詰まり
            </h2>
          </div>
        </div>
        <ul className="mt-8 grid gap-4 md:grid-cols-2">
          {items.map((t) => (
            <li
              key={t}
              className="rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-4 text-left text-base leading-relaxed text-[#18181B]"
            >
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
