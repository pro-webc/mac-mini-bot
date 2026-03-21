import { Target, HeartHandshake, Gauge } from "lucide-react";

const items = [
  "安全を、注意の量ではなく再現できる行動に変える",
  "評価は改善の材料にし、個人攻撃にしない",
  "社内の実情に合わせて、無理のない頻度と尺を提案する",
];

export default function TsHubStdAboutPhilosophySection() {
  const icons = [Target, HeartHandshake, Gauge];
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="philosophy-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="philosophy-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          大切にしていること
        </h2>
        <ul className="mt-10 flex flex-col gap-4">
          {items.map((text, i) => {
            const Icon = icons[i] ?? Target;
            return (
              <li
                key={text}
                className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-5"
              >
                <Icon className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
                <p className="text-left text-base leading-[1.7] text-[#0F172A]">{text}</p>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
