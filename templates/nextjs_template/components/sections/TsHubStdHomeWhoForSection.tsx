import { Building2, CalendarClock, Monitor } from "lucide-react";

const bullets = [
  {
    text: "社用車を複数台保有し、社内教育をもう一段、仕組みとして強化したい",
    Icon: Building2,
  },
  {
    text: "朝礼やミーティングで、短い話題として毎週使えるネタが欲しい",
    Icon: CalendarClock,
  },
  {
    text: "まずはオンラインで、打ち合わせから始めたい",
    Icon: Monitor,
  },
];

export default function TsHubStdHomeWhoForSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="who-for-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="who-for-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          こんな法人さまに相談いただいています
        </h2>
        <ul className="mt-10 flex flex-col gap-4">
          {bullets.map((b) => (
            <li
              key={b.text}
              className="flex gap-4 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-5"
            >
              <b.Icon
                className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]"
                aria-hidden
              />
              <p className="text-left text-base leading-[1.7] text-[#0F172A]">
                {b.text}
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-8 max-w-prose text-left text-sm leading-relaxed text-[#64748B]">
          車両台数や運用形態によって最適な進め方が変わります。優先して支援したいケースがある場合もあるため、まずは状況をお聞かせください。
        </p>
      </div>
    </section>
  );
}
