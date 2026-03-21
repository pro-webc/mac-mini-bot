import { Ban } from "lucide-react";

export default function TshProgramLimitationsSection() {
  const bullets = [
    "法令解釈やコンプライアンス判断の代替",
    "監督官庁の指導の代替",
    "医療的判断",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="limitations-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="limitations-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          できないこと
        </h2>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 border border-[#e7e5e4] bg-[#fafaf9] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <Ban className="mt-0.5 h-6 w-6 shrink-0 text-[#57534e]" aria-hidden />
              <span>{t}</span>
            </li>
          ))}
        </ul>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          必要な専門領域は、適切な専門家へお願いします。
        </p>
      </div>
    </section>
  );
}
