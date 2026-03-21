type FlowVariant = "services" | "process";

type Phase = { label: string; note: string };

const servicesPhases: Phase[] = [
  {
    label: "現地調査",
    note: "設置環境・制約・関係者の前提を整理し、安全上の留意点を共有します。",
  },
  {
    label: "設計・段取り",
    note: "設計意図と現地条件を踏まえ、工程と役割分担のたたき台を作ります。",
  },
  {
    label: "設置・配線・接続",
    note: "機器・配線・接続作業を手順に沿って進め、確認ポイントを都度記録します。",
  },
  {
    label: "試験・調整",
    note: "つながり状態の確認と調整を行い、引き渡し条件に向けてすり合わせます（範囲は案件により異なります）。",
  },
  {
    label: "保守",
    note: "運用開始後の相談窓口や定期対応の切り分けは、契約条件に基づき事前合意します。",
  },
];

const processPhases: Phase[] = [
  { label: "相談受付", note: "フォーム・電話で状況と希望時期を伺い、次の確認項目を共有します。" },
  { label: "現地確認", note: "必要に応じて現地を確認し、制約とリスクを可視化します。" },
  { label: "提案・見積", note: "範囲・工程・前提条件を文章化し、見積のたたき台をご提示します。" },
  { label: "工程計画", note: "許認可・協力体制・報告タイミングを含め、実行計画を固めます。" },
  { label: "実施", note: "手順と安全管理のもとで作業を進め、変化があれば都度共有します。" },
  { label: "試験", note: "接続状態や動作確認の観点をすり合わせ、合格基準に向けて調整します。" },
  { label: "引き渡し", note: "引き渡し範囲と残課題を整理し、運用側との接続を支援します。" },
  { label: "保守相談", note: "運用後の相談窓口や定期対応の可否は、契約条件を確認のうえ設計します。" },
];

type Props = {
  variant?: FlowVariant;
};

export default function ServiceFlowSection({ variant = "services" }: Props) {
  const phases = variant === "process" ? processPhases : servicesPhases;
  const heading =
    variant === "process" ? "進め方（ご相談〜引き渡し〜保守相談）" : "工程の詳細（調査〜保守）";
  const intro =
    variant === "process"
      ? "案件により前後・省略があります。初回ヒアリングで無理のない計画を一緒に組み立てます。"
      : "通信設備のライフサイクルに沿って、調査から試験調整、保守相談までを支援します。前後する場合は都度ご説明します。";

  return (
    <section className="mt-12 px-0 py-12 md:py-16" aria-labelledby={`flow-heading-${variant}`}>
      <div className="mx-auto max-w-6xl">
        <h2
          id={`flow-heading-${variant}`}
          className="text-2xl font-bold tracking-tight text-white md:text-3xl"
        >
          {heading}
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#BFDBFE]">{intro}</p>
        <div className="mt-10 overflow-x-auto">
          <ol
            className={`flex min-w-0 list-none flex-col gap-3 md:grid ${
              variant === "process"
                ? "md:grid-cols-2 lg:grid-cols-4"
                : "md:grid-cols-5"
            }`}
          >
            {phases.map((p, i) => (
              <li
                key={`${variant}-${p.label}`}
                className="flex flex-1 flex-col rounded-[12px] border border-white/20 bg-[#1e40af] p-4"
              >
                <span className="text-xs font-bold text-[#caeb25]">STEP {i + 1}</span>
                <p className="mt-2 text-base font-semibold text-white">{p.label}</p>
                <p className="mt-2 text-left text-sm text-[#E0E7FF]">{p.note}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
