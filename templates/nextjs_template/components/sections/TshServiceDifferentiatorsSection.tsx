import { Users } from "lucide-react";

export default function TshServiceDifferentiatorsSection() {
  const bullets = [
    "気づきを共有する問いかけ",
    "具体例の持ち寄り",
    "ファシリテーションの役割",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="diff-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="diff-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          ティーチング偏重になりがちな場面での工夫
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
          進行の特徴を、他社比較ではなく「現場で再現しやすい形」に寄せています。
        </p>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 border border-[#e7e5e4] bg-[#fafaf9] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <Users
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
