const fullFaq = [
  {
    question: "オンラインでも実施できますか？",
    answer:
      "可能な場合があります。対象者の分散状況、演習の可否、機器の扱いにより最適解が変わるため、まずは現状を伺います。",
  },
  {
    question: "人数に制限はありますか？",
    answer:
      "設計により異なります。少人数からの試行も可能です。まずは想定人数と会場条件（オンライン比率含む）をお知らせください。",
  },
  {
    question: "費用はいくらですか？",
    answer:
      "内容・時間・回数・移動範囲により変動します。お問い合わせ後にヒアリングし、見積のたたき台をご提示します（確定値の事前掲載は要方針確認）。",
  },
  {
    question: "GPSの評価は個人を追い詰めませんか？",
    answer:
      "採点競争にしない進行を原則とし、振り返りと改善の材料として扱います。説明範囲・保存期間・共有者は事前に合意します。",
  },
  {
    question: "朝礼ネタは本当にそのまま使えますか？",
    answer:
      "短い問いかけとチェック観点を中心に提供します。社内規程・現場文化に合わせて言い換えてください。必要なら言い回しの調整も相談できます。",
  },
  {
    question: "鹿児島以外も対応できますか？",
    answer:
      "主商圏は鹿児島市周辺です。遠方はオンライン中心など条件次第です。まずは希望エリアと実施イメージをお知らせください。",
  },
];

export default function KgsContactPageHeaderSection() {
  const intro = [
    "お問い合わせ後、3営業日以内に返信（目安。実運用で確定）",
    "日程調整は外部予約ツールへ（アカウント取得は別途）",
    "自動返信の有無は実装時に設定（仕様としては推奨）",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-contact-header-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="kgs-contact-header-h1"
          className="text-left text-3xl font-bold tracking-tight text-[#18181B] md:text-4xl"
        >
          お問い合わせ・面談予約
        </h1>
        <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-relaxed text-[#18181B]">
          {intro.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>

        <div id="faq-full" className="mt-14 scroll-mt-28">
          <h2 className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl">
            よくある質問
          </h2>
          <div className="mt-8 space-y-6">
            {fullFaq.map((f) => (
              <article
                key={f.question}
                className="border border-[#E4E4E7] bg-[#FAFAF9] p-5"
              >
                <h3 className="text-left text-lg font-semibold text-[#18181B]">
                  {f.question}
                </h3>
                <p className="mt-3 text-left text-base leading-relaxed text-[#18181B]">
                  {f.answer}
                </p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
