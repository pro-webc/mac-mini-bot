import { HeartHandshake } from "lucide-react";

export default function KgsAboutPhilosophySection() {
  const items = [
    "運転者を貶めず、改善に繋がる対話を守る",
    "説得ではなく、本人の言語化とチーム学習を促す",
    "測定は支配ではなく、振り返りの材料にする",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-about-phil-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-about-phil-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          大切にしていること
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <HeartHandshake
                className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]"
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
