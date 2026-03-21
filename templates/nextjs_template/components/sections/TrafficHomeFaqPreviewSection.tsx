import Link from "next/link";
import { ArrowRight, HelpCircle } from "lucide-react";

const faq = [
  {
    q: "オンラインでも実施できますか？",
    a: "ハイブリッドやオンライン要素の組み込みは、目的と参加者環境に応じてご相談ください。最適な形は事前ヒアリングで一緒に決めます。",
  },
  {
    q: "対象人数や最小催行はありますか？",
    a: "当面は、社用車を複数台運用する企業の場を想定しています。人数や開催条件は、会場・時間・評価方法に連動するため、お問い合わせ時に個別にすり合わせます。",
  },
  {
    q: "自車走行の評価では、どんなデータを扱いますか？",
    a: "走行傾向を把握するための位置情報や行動ログ等を用いる想定です。取得範囲・保管・削除方針は、貴社の規程と合わせて事前に説明し、同意の上で進めます（確定文言は別途整備）。",
  },
  {
    q: "料金はどのくらいですか？",
    a: "研修時間、回数、人数、移動範囲、評価の有無により変動します。お問い合わせ後に、目的に沿ったプランとお見積りをご提示します。",
  },
  {
    q: "他社の研修との違いは何ですか？",
    a: "他社を評価する立場ではありません。当方の特徴は、習慣の言語化・共有を核に据えた進行と、評価による観点整理を組み合わせ、説明責任を高める設計にあります。",
  },
  {
    q: "公開できる実績や社名はありますか？",
    a: "現在は一般化した説明に留めています。公開許諾が得られた事例は、順次掲載できるよう準備します。",
  },
];

export default function TrafficHomeFaqPreviewSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-faq-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <HelpCircle className="mt-1 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
          <div className="min-w-0 flex-1">
            <h2
              id="traffic-faq-heading"
              className="text-left font-semibold leading-[1.35] text-[#18181B]"
              style={{
                fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
                fontWeight: 650,
              }}
            >
              よくある質問（抜粋）
            </h2>
            <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
              オンライン可否。対象人数・最小催行。準備物（自車走行の場合）。個人情報・走行データの扱い（方針レベル）。
            </p>
          </div>
        </div>
        <div className="mt-10 space-y-3 max-w-prose">
          {faq.map(({ q, a }) => (
            <details
              key={q}
              className="group rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-4 open:bg-[#FFFFFF] motion-safe:transition-colors"
            >
              <summary className="cursor-pointer list-none text-left font-semibold text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] [&::-webkit-details-marker]:hidden">
                <span className="inline-flex w-full items-start justify-between gap-3">
                  <span className="min-w-0">{q}</span>
                  <span className="shrink-0 text-sm font-medium text-[#0F766E] group-open:hidden">
                    開く
                  </span>
                  <span className="hidden shrink-0 text-sm font-medium text-[#0F766E] group-open:inline">
                    閉じる
                  </span>
                </span>
              </summary>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {a}
              </p>
            </details>
          ))}
        </div>
        <div className="mt-10">
          <Link
            href="/contact"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] transition-colors hover:bg-[#F4F4F5] active:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488] motion-safe:transition-colors"
          >
            FAQをもっと見る
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </Link>
        </div>
      </div>
    </section>
  );
}
