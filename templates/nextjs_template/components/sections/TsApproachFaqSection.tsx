import Link from "next/link";
import { ChevronRight, HelpCircle } from "lucide-react";

const faqPairs = [
  {
    q: "オンラインでも実施できますか？",
    a: "案件により検討します。集合・オンサイト・オンライン要素の併用など、最適な形はヒアリングのうえで提案します。",
  },
  {
    q: "対象は運輸業（緑ナンバー）だけですか？",
    a: "いいえ。当面は白ナンバー中心の事業用車運用企業の管理部門から入り、整備後に運輸系へ広げる想定です。",
  },
  {
    q: "人数に制限はありますか？",
    a: "一人対応の事業のため、実施形式や日程により調整します。まずは人数・拠点数・希望時期をお知らせください。",
  },
  {
    q: "料金はいくらですか？",
    a: "内容・回数・実施場所により個別見積です。貴社の運用状況を伺ったうえで、無理のない入り方をご提案します。",
  },
  {
    q: "週1のアドバイスは誰が書きますか？",
    a: "原則担当（羽生）の監修原稿を基に、制作枠で掲載します。文体と分量はサイト上で統一します。",
  },
  {
    q: "機材や評価の詳細は公開されますか？",
    a: "公開範囲は相談しながら決めます。秘匿が必要な部分は、相談時に口頭・資料で補足します。",
  },
];

export default function TsApproachFaqSection() {
  return (
    <section
      className="bg-[#F4F4F5] py-16 md:py-20"
      aria-labelledby="approach-faq-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="approach-faq-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          進め方に関するよくある質問
        </h2>
        <ul className="mt-6 space-y-3 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
          <li className="flex gap-2 text-left text-sm text-[#52525B] md:text-base">
            <HelpCircle className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]" aria-hidden />
            <span>機材や評価ロジックの開示範囲は相談しながら決める</span>
          </li>
          <li className="flex gap-2 text-left text-sm text-[#52525B] md:text-base">
            <HelpCircle className="mt-0.5 h-5 w-5 shrink-0 text-[#0F766E]" aria-hidden />
            <span>オンライン実施の可否は案件次第</span>
          </li>
        </ul>
        <div className="mt-8">
          <Link
            href="/approach#faq-detail"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#0F766E] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#0F766E] hover:bg-[#FAFAF9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
          >
            FAQを見る
            <ChevronRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
        <div id="faq-detail" className="mt-10 space-y-4 scroll-mt-24">
          {faqPairs.map(({ q, a }) => (
            <article
              key={q}
              className="border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6"
            >
              <h3 className="text-left text-base font-semibold text-[#18181B]">
                {q}
              </h3>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {a}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
