import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function ProgramPageContent() {
  return (
    <>
      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h1 className="text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl">
            講習プログラム
          </h1>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
            対象、実施形態、当日の進行、準備物までを一ページで把握できるように整理しました。細部は貴社の運用に合わせて調整します。
          </p>
          <div className="mt-10">
            <ImagePlaceholder
              aspectClassName="aspect-video"
              overlayText="当日の進行イメージ（タイムライン）"
              description="横長・ホワイトボードに番号付きの6ステップが並んだ写真イメージ。各ステップは短い見出しのみ。会議室、清潔、人物は後ろ姿中心。"
            />
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            対象
          </h2>
          <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              白ナンバーの事業用車を複数台お持ちの企業（目安としておおむね20台以上の規模感から設計可能）
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              安全運転管理者・運行管理担当者の方が中心となり、社内の安全活動に関わる組織
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            集合／オンサイト／オンライン併用など、条件に合わせて最適化します
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            会場、参加人数、勤務シフト、複数拠点の有無によって最適解が変わります。事前面談で制約を整理し、無理のない回数と時間配分をご提案します。
          </p>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              集合研修（半日〜1日型）
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              拠点訪問型（運行の実情に合わせた短時間×複数回）
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              オンラインを組み合わせたハイブリッド（運用負担を抑える配分）
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            当日の進行（例）
          </h2>
          <ol className="mt-8 max-w-prose list-decimal space-y-3 pl-5 text-left text-base leading-[1.7] text-[#0f172a]">
            <li>目的と進行ルールの合意（短時間）</li>
            <li>気づき共有のための問いかけとミニワーク</li>
            <li>可視化を用いた理解のすり合わせ</li>
            <li>一般道路の走行を前提とした評価の視点のインプット</li>
            <li>管理者向け：翌週以降の振り返りに使う質問例のお渡し</li>
            <li>質疑応答・次のステップ確認</li>
          </ol>
          <p className="mt-6 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            内容は参加層・時間・会場に応じて増減します。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            準備物（参加者・管理者）
          </h2>
          <div className="mt-8 grid gap-8 md:grid-cols-2">
            <div className="border border-[#e7e5e4] bg-[#fafaf9] p-6">
              <h3 className="text-lg font-bold text-[#0f172a]">参加者</h3>
              <ul className="mt-4 space-y-2 text-left text-sm leading-[1.7] text-[#57534e]">
                <li>筆記用具</li>
                <li>社内規程で許可される範囲のメモ手段（スマートフォン等）</li>
              </ul>
            </div>
            <div className="border border-[#e7e5e4] bg-[#fafaf9] p-6">
              <h3 className="text-lg font-bold text-[#0f172a]">
                管理者・ご担当者
              </h3>
              <ul className="mt-4 space-y-2 text-left text-sm leading-[1.7] text-[#57534e]">
                <li>直近の安全活動の課題感（箇条書きで可）</li>
                <li>車両保有台数・運用の概要（拠点、シフト、典型ルートなど）</li>
                <li>これまでの教育・講習の実施履歴（分かる範囲）</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionPad} border-b-0 bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            管理者向け：よくある論点
          </h2>
          <dl className="mt-8 space-y-8">
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                受講後、現場に戻したいのですが何から始めればいいですか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                まずは朝礼の1問だけ置き換えるのが効果的です。当日お渡しする「短い問いの型」から選び、2週間試してください。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                評価は個人に付けますか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                目的は改善の支援です。個人攻撃に寄らない運用を前提に、記録の粒度と共有範囲を事前に合意します。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                オンラインだけでも意味がありますか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                可能です。ただし体感要素が弱くなる分、短時間の反復や、現場写真・動画（社内規程の範囲）を組み合わせる設計が有効です。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                最小・最大の人数に決まりはありますか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                現場条件によります。面談で人数と会場を伺い、進行が成立する形を提案します。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                費用はどの段階で分かりますか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                実施形態・回数・移動範囲が固まった段階でお見積りします。先に上限感の希望があれば、そこから逆算してプランを組みます。
              </dd>
            </div>
          </dl>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
          </div>
        </div>
      </section>
    </>
  );
}
