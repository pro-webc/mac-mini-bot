export default function TshHomeProcessTeaserSection() {
  const steps = [
    "無料相談：課題と制約（車両台数、日程、拠点）を伺います",
    "すり合わせ：実施形態と範囲を提案します",
    "ご契約・準備：参加者条件やルートの確認を行います",
    "実施・振り返り：現場に戻った後の定着も一緒に設計します",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="process-teaser-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="process-teaser-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          ご利用の流れ
        </h2>
        <ol className="mt-10 grid gap-4 md:grid-cols-2">
          {steps.map((s, i) => (
            <li
              key={s}
              className="flex gap-4 border border-[#e7e5e4] bg-[#ffffff] p-5"
            >
              <span
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#0f766e] text-sm font-bold text-[#ffffff]"
                aria-hidden
              >
                {i + 1}
              </span>
              <p className="text-left text-base leading-[1.7] text-[#1c1917]">
                {s}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
