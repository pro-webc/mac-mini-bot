import { CircleCheck } from "lucide-react";

export default function TshHomeTrustStripSection() {
  const bullets = [
    "一方通行の説明だけでは、行動が変わりにくい場面がある",
    "チームで言語化すると、ルールが「自分の話」になる",
    "データは補助であり、最終判断や監督の代替ではありません",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="trust-strip-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="trust-strip-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          まず、前提をそろえます
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          安全運転は、知識を入れた瞬間に習慣へ変わるものではありません。現場の会話と、継続の仕組みがあるほど定着しやすくなります。
        </p>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 rounded-none border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <CircleCheck
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
