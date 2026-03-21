import { MessageCircleWarning } from "lucide-react";

export default function TshHomePainSympathySection() {
  const bullets = [
    "朝礼のネタが毎回似たり寄ったりで、現場の反応が薄い",
    "指導が続くほど、対話ではなく伝達になりがち",
    "改善点が個人に閉じて、組織としての学びに繋がりにくい",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="pain-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="pain-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          安全管理の現場で、こんな詰まりはありませんか
        </h2>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 rounded-none border border-[#e7e5e4] bg-[#fafaf9] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <MessageCircleWarning
                className="mt-0.5 h-6 w-6 shrink-0 text-[#0f766e]"
                aria-hidden
              />
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
