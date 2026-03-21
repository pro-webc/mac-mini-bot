import Link from "next/link";
import { GitBranch, Headphones, ShieldCheck } from "lucide-react";

const pillars = [
  {
    title: "品質の考え方",
    body: "手順と確認を重ね、関係法令・現場ルールを踏まえた作業を基本とします。断定過多の約束は避け、範囲は都度すり合わせます。",
    icon: ShieldCheck,
  },
  {
    title: "連絡体制",
    body: "状況変化が出たときに遅れないよう、報告経路と優先度を早い段階で共有します。オンラインと現場のハイブリッドにも対応します。",
    icon: Headphones,
  },
  {
    title: "変更管理",
    body: "工程や仕様の変更が生じた場合は、影響範囲と選択肢を短い文章で整理し、合意形成を優先します。",
    icon: GitBranch,
  },
];

export default function TrustSignalsSection() {
  return (
    <section className="mt-12 px-0 py-12 md:py-16" aria-labelledby="trust-signals-page-heading">
      <div className="mx-auto max-w-6xl">
        <h2
          id="trust-signals-page-heading"
          className="text-2xl font-bold tracking-tight text-white md:text-3xl"
        >
          品質・連絡・変更への向き合い方
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#BFDBFE]">
          インフラ工事では、現場条件の変化が前提です。以下は運用イメージのたたき台であり、正式条件はお問い合わせ時にご説明します。
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
          <Link
            href="/contact"
            className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            お問い合わせフォーム
          </Link>
          から、具体的な状況をお送りください。
        </p>
      </div>
    </section>
  );
}
