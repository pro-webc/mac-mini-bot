const steps = [
  {
    title: "お問い合わせ",
    text: "フォームから課題の概要、希望時期、対象者のイメージを送ってください。",
  },
  {
    title: "初回ヒアリング",
    text: "オンライン面談などで、実施形式・範囲・安全上の注意を確認します。",
  },
  {
    title: "提案",
    text: "内容、回数、進行案を文章でご提示します。",
  },
  {
    title: "契約・日程調整",
    text: "実施日、集合方法、社内連絡フローを確定します。",
  },
  {
    title: "実施",
    text: "講習・ワーク、必要に応じて評価を実施します。",
  },
  {
    title: "振り返り",
    text: "次の運用に繋げるアクションを短く整理します。",
  },
];

export default function TsHubStdProcessStepsSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="steps-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="steps-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          ステップ
        </h2>
        <div className="mt-10 overflow-x-auto md:overflow-visible">
          <ol className="flex min-w-[640px] flex-row gap-0 md:min-w-0 md:grid md:grid-cols-3 lg:grid-cols-6">
            {steps.map((s, i) => (
              <li
                key={s.title}
                className="flex min-w-[200px] flex-1 flex-col border border-[#E2E8F0] bg-[#FFFFFF] p-4 md:min-w-0"
              >
                <span className="text-xs font-bold uppercase tracking-wide text-[#0F766E]">
                  Step {i + 1}
                </span>
                <h3 className="mt-2 text-lg font-semibold text-[#0F172A]">
                  {s.title}
                </h3>
                <p className="mt-2 text-left text-sm leading-relaxed text-[#64748B]">
                  {s.text}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
