import { CheckCircle2 } from "lucide-react";

const bullets = [
  "約30年にわたる関連業務の経験を踏まえ、会社ごとに異なる運用実態へ寄り添います。",
  "一方的な説教に偏らない進行で、参加者が自ら言語化できる時間をつくります。",
  "運転の良し悪しを感覚だけにせず、評価と振り返りまでをセットで設計します（内容・条件は事前すり合わせ）。",
];

export default function TsHubHomeTrustStripSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          支援のスタンス
        </h2>
        <ul className="mt-8 grid gap-4 md:grid-cols-3">
          {bullets.map((text) => (
            <li
              key={text}
              className="flex gap-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 sm:p-5"
            >
              <CheckCircle2
                className="mt-0.5 h-6 w-6 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <p className="text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {text}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
