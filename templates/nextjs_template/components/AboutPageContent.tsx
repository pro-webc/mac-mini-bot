import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function AboutPageContent() {
  return (
    <>
      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h1 className="text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl">
            講師・事業について
          </h1>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
            この事業は、鹿児島市エリアを主戦場に、企業の交通安全教育に集中して取り組んでいます。全国規模の大量集客より、地元企業の運用に寄り添うことを優先します。
          </p>
          <div className="mt-10">
            <ImagePlaceholder
              aspectClassName="aspect-[4/3]"
              overlayText="現場経験に根ざした伴走のイメージ"
              description="中近景・講師がホワイトボードの横に立ち、短い問いを書き留めている様子。服装はビジネスカジュアル。表情は穏やか。背景はシンプルな会議室。過度な演出なし。"
            />
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            約30年にわたる現場経験を土台に、企業の安全管理の現実に合わせて伴走します
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            長年にわたり、運転や交通に関わる現場に身を置いてきました。事故現場への対応や、企業内での安全運転管理の課題には、机上の正論だけでは届かない局面があることも理解しています。だからこそ、講義の正確さだけでなく、現場に戻ったあと続く「短い振り返り」と「共通の言葉」までをセットで設計します。
          </p>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              企業の安全運転管理者・運行管理担当者の立場に立った説明を心がける
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              誇大な効果や断定は避け、運用に耐える現実的な提案に寄せる
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              機材・手順・評価は、貴社の体制と負担に合わせて調整する
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            いま強化している領域と、将来の拡張
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            現フェーズでは、白ナンバーの事業用車を複数台お持ちの企業さまを主な対象としています。運輸（緑ナンバー）領域は、将来的な展開として検討可能ですが、主戦場と矛盾しない形で段階的に整理します。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} border-b-0 bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            信頼の根拠（表現の方針）
          </h2>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              具体的な社名、受講実績数、事故率削減の数値など、未確認の事実は掲載しません
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              警察・行政との公式関係を暗示する表現は使いません
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              第三者ロゴや推薦文は、契約と権利が確認できたもののみ
            </li>
          </ul>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href="/service">サービス・強みを見る</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
          </div>
        </div>
      </section>
    </>
  );
}
