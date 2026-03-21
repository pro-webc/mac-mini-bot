import Link from "next/link";
import { Building2, RadioTower, Users } from "lucide-react";

const pillars = [
  {
    title: "現場起点の品質",
    body: "手順と確認を重ね、関係法令・現場ルールを踏まえた作業を基本とします（詳細条件は案件ごとに調整）。",
    icon: RadioTower,
  },
  {
    title: "小さなチームの機動力",
    body: "意思決定までの距離を短く、状況変化にも素早く寄り添う体制を目指します（訴求はデモ仮説）。",
    icon: Users,
  },
  {
    title: "インフラの文脈で伴走",
    body: "親会社グループの事業領域の知見を参照しつつ、ワン・ピースとして最適な実行計画を相談します（公式表記は整理後に確定）。",
    icon: Building2,
  },
];

export default function HomeTrustSignalsSection() {
  return (
    <section className="mt-12 px-0 py-12 md:py-16" aria-labelledby="trust-heading">
      <div className="mx-auto max-w-6xl">
        <h2
          id="trust-heading"
          className="text-2xl font-bold tracking-tight text-white md:text-3xl"
        >
          現場品質・スピード・伴走の考え方
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#BFDBFE]">
          建設業界の旧来イメージにとらわれず、シンプルで勢いのあるコミュニケーションを大切にします。数値実績の断定はせず、工程と対応の考え方で厚みを作ります。
        </p>
        <ul className="mt-10 grid gap-6 md:grid-cols-3">
          {pillars.map((p) => {
            const Icon = p.icon;
            return (
              <li
                key={p.title}
                className="flex flex-col rounded-[12px] border border-white/20 bg-[#1e40af] p-6"
              >
                <Icon className="h-8 w-8 text-[#caeb25]" aria-hidden />
                <h3 className="mt-4 text-lg font-semibold text-white">{p.title}</h3>
                <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">{p.body}</p>
              </li>
            );
          })}
        </ul>
        <p className="mt-8 text-left text-sm text-[#BFDBFE]">
          親会社グループの取り組みは参考として{" "}
          <Link
            href="https://task888.com/"
            rel="noopener noreferrer"
            target="_blank"
            className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            task888.com
          </Link>
          ／
          <Link
            href="https://task888-recruit.com/"
            rel="noopener noreferrer"
            target="_blank"
            className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            task888-recruit.com
          </Link>
          をご覧ください（表記・素材は公開前に整備します）。
        </p>
      </div>
    </section>
  );
}
