import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function ScalePage() {
  return (
    <div className="w-full">
      <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-[#0f172a] md:text-4xl">
                対象と想定規模
              </h1>
              <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                全国規模の大量集客ではなく、地元法人の担当者が業務の合間に理解し、後日見返せる説明の置き場として設計しています。
              </p>
            </div>
            <div className="w-full max-w-full">
              <ImagePlaceholder
                aspectClassName="aspect-[4/3]"
                overlayText="複数台運用の法人イメージ（鹿児島エリア）"
                description="4:3。駐車場に並ぶ白ナンバーの社用車が手前に数台、背景に事業所。人物は後ろ姿またはフレーム外。"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            社用車を複数台お持ちの法人様
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            営業車、サービス車、公用車など、白ナンバーを中心とした社用車運用が前提の組織を想定しています。安全運転管理者制度の観点だけでなく、現場の運転習慣と管理の両方に手を入れたい場合に相性が良いです。
          </p>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#ffffff]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            目安：おおむね20台以上
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            制度上の義務の話だけでなく、複数台の運転特性が混ざるほど、共通言語と評価の見方があると現場が動きやすくなる、という観点で設計できます。台数が少ない場合でも、運用の複雑さが高いケースはご相談ください。
          </p>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            主な対応エリア
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            鹿児島市を主軸に、周辺エリアの法人様からのご相談も受け付けます。移動条件や実施形態は、事前にすり合わせます。
          </p>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#ffffff]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            運送事業者様について
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            運送系特有の論点は段階的に扱えるよう、内容の深度を調整します。いきなり広い範囲を約束するのではなく、貴社の現場に合わせて拡張します。
          </p>
        </div>
      </section>

      <section className={`${sectionY} bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            規模と運用を伺い、無理のない形を提案します
          </h2>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>相談予約</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
          </div>
        </div>
      </section>
    </div>
  );
}
