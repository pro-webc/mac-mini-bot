import { LayoutGrid } from "lucide-react";

export default function TshProgramFormatsSection() {
  const bullets = [
    "半日：導入〜ワーク〜振り返り",
    "分割：週次で短時間×複数回",
    "オンライン併用：目的次第で設計（可否は相談）",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="prog-formats-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="prog-formats-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          実施形態の例
        </h2>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 border border-[#e7e5e4] bg-[#fafaf9] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <LayoutGrid
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
