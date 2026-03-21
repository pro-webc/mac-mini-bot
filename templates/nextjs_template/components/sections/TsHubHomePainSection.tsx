import { AlertCircle } from "lucide-react";

const items = [
  "朝礼の話が毎週似た内容になり、現場の反応が薄い",
  "部門ごとにノウハウがバラつき、横展開がしづらい",
  "講義中心だと「分かったつもり」で終わり、行動が変わりにくい",
  "運転評価が主観に寄り、何から直すか決めづらい",
];

export default function TsHubHomePainSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          こんな手応えのなさ、ありませんか
        </h2>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2">
          {items.map((t) => (
            <li
              key={t}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4"
            >
              <AlertCircle
                className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <p className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
                {t}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
