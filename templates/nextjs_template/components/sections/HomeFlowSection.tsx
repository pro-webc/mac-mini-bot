import { Activity, Cable, ClipboardList, Hammer, Search } from "lucide-react";

const steps = [
  {
    step: "1",
    title: "現地調査",
    body: "設置環境・制約・関係者の前提を整理し、安全上の留意点を共有します（一般例）。",
    icon: Search,
  },
  {
    step: "2",
    title: "段取り",
    body: "工程・役割・報告タイミングのたたき台を作り、認識合わせを進めます。",
    icon: ClipboardList,
  },
  {
    step: "3",
    title: "設置・接続",
    body: "機器・配線・接続作業を手順に沿って実施し、確認ポイントを都度記録します。",
    icon: Hammer,
  },
  {
    step: "4",
    title: "試験調整",
    body: "つながり状態の確認と調整を行い、引き渡し条件に向けてすり合わせます（範囲は案件により異なります）。",
    icon: Activity,
  },
  {
    step: "5",
    title: "保守",
    body: "運用開始後の相談窓口や定期対応の切り分けは、契約条件に基づき事前合意します。",
    icon: Cable,
  },
];

export default function HomeFlowSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="home-flow-heading"
    >
      <h2
        id="home-flow-heading"
        className="text-center text-xl font-bold text-[#0F172A] md:text-left md:text-2xl"
      >
        工事の流れ（デモ用の一般例）
      </h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-base leading-relaxed text-[#475569] md:mx-0 md:text-left">
        現地調査から段取り、設置・接続、試験調整、保守相談までをイメージしやすいよう整理しています。案件により前後します。
      </p>
      <ol className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {steps.map((s) => {
          const Icon = s.icon;
          return (
            <li
              key={s.step}
              className="flex flex-col gap-3 rounded-none border border-[#E2E8F0] bg-[#F8FAFC] p-4"
            >
              <div className="flex flex-wrap items-center gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[#caeb25] bg-[#F7FEA8] text-sm font-bold text-[#0F172A]">
                  {s.step}
                </span>
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[#1d4ed8]/40 bg-[#EFF6FF] text-[#1d4ed8]">
                  <Icon className="h-5 w-5" aria-hidden />
                </span>
                <h3 className="text-lg font-bold text-[#0F172A]">{s.title}</h3>
              </div>
              <p className="text-left text-sm leading-relaxed text-[#475569]">{s.body}</p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
