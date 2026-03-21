const steps = [
  "STEP1：現状ヒアリング（運用・事故リスクの捉え方・朝礼の実態）",
  "STEP2：対話セッション（意識の立ち上がり方の言語化と共有）",
  "STEP3：可視化フィードバック（見える化で気づきを作る）",
  "STEP4：道路評価（自社車両・一般道コース、スコアと減点理由の説明）",
  "STEP5：改善計画（小さな運用変更から）",
];

export default function TsProcessDiagramSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="process-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="process-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          プロセス全体（図解はマークアップ＋Tailwind）
        </h2>
        <ol className="mt-10 space-y-0">
          {steps.map((label, i) => {
            const idx = label.indexOf("：");
            const stepTitle = idx >= 0 ? label.slice(0, idx) : label;
            const stepBody = idx >= 0 ? label.slice(idx + 1) : "";
            return (
              <li key={label} className="relative flex gap-0">
                <div className="flex w-10 shrink-0 flex-col items-center md:w-12">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-[#0F766E] bg-[#FFFFFF] text-sm font-semibold text-[#0F766E] md:h-12 md:w-12 md:text-base">
                    {i + 1}
                  </div>
                  {i < steps.length - 1 ? (
                    <div
                      className="my-1 w-0 flex-1 border-l-2 border-dashed border-[#E4E4E7]"
                      aria-hidden
                    />
                  ) : null}
                </div>
                <div className="grow pb-8 pl-4 md:pl-6">
                  <div className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-5">
                    <h3 className="text-base font-semibold text-[#18181B]">
                      {stepTitle}
                    </h3>
                    <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                      {stepBody}
                    </p>
                  </div>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
