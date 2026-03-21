import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function ColumnPageContent() {
  return (
    <>
      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h1 className="text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl">
            お役立ちコラム（朝礼ネタ）
          </h1>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
            毎週、短時間で読める「一口アドバイス」を更新します。安全運転管理者の方が、そのまま朝礼や短いミーティングに転用しやすい言い回しを意識して執筆します。
          </p>
          <div className="mt-10">
            <ImagePlaceholder
              aspectClassName="aspect-[5/2]"
              overlayText="短い記事が週次で積み上がるイメージ"
              description="ワイド・机上に数枚のA4メモが扇状に広がり、各枚に短い見出しのみ。ペン、コーヒーカップの縁。自然光、落ち着いたオフィス。人物なしでも可。"
            />
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            一覧の見せ方（運用ルール）
          </h2>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              カード一覧：タイトル／要約／公開日／タグ
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              タグ例：朝礼、管理者、視線、評価、対話、振り返り、荷役、駐車、雨天
            </li>
          </ul>
          <p className="mt-6 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            記事本文は読みやすい長さに抑え、最後に「明日の朝礼で使う一言」を必ず置きます。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <article className="border border-[#e7e5e4] bg-[#fafaf9] p-6 md:p-10">
            <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl">
              朝礼1分：合流地点で「速度差」を先に見る
            </h2>
            <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
              合流は、譲り合い以前に速度差が崩れると危険が跳ね上がります。短い合言葉で揃えるポイントをまとめます。
            </p>
            <h3 className="mt-8 text-lg font-bold text-[#0f172a]">本文（要点）</h3>
            <ul className="mt-4 max-w-prose space-y-2 text-left text-base leading-[1.7] text-[#0f172a]">
              <li>合流手前で、まず「自分の速度が流れに乗っているか」を確認する</li>
              <li>ミラーの順番を決め、急な方向転換を減らす</li>
              <li>合流後は、一度車間を作ってから車線変更を検討する</li>
            </ul>
            <p className="mt-8 border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base font-semibold text-[#0f766e]">
              明日の朝礼で使う一言：「合流は、譲る前に速度差をなくす。」
            </p>
            <p className="mt-4 text-sm text-[#57534e]">タグ：朝礼／合流／速度差</p>
          </article>

          <article className="mt-12 border border-[#e7e5e4] bg-[#fafaf9] p-6 md:p-10">
            <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl">
              管理者向け：注意が刺さらない日の“次の一手”
            </h2>
            <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
              同じ注意が続くとき、ルールの再掲だけに寄せない方が現場は動きます。短い対話の型を一つ足す方法です。
            </p>
            <h3 className="mt-8 text-lg font-bold text-[#0f172a]">本文（要点）</h3>
            <ul className="mt-4 max-w-prose space-y-2 text-left text-base leading-[1.7] text-[#0f172a]">
              <li>「何が起きやすい場面か」を一つに絞る</li>
              <li>再発条件を「環境・時間帯・荷物・天候」に分解する</li>
              <li>翌週、同じ問いを繰り返して変化を観察する</li>
            </ul>
            <p className="mt-8 border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base font-semibold text-[#0f766e]">
              明日の朝礼で使う一言：「今日は、昨日より一つだけ違う所作を試す。」
            </p>
            <p className="mt-4 text-sm text-[#57534e]">タグ：管理者／対話／振り返り</p>
          </article>

          <article className="mt-12 border border-[#e7e5e4] bg-[#fafaf9] p-6 md:p-10">
            <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl">
              評価メモ：良い運転は「状況が違っても再現できるか」
            </h2>
            <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
              褒めるポイントを行動に落とすと、次の週の振り返りが速くなります。メモの粒度の例を紹介します。
            </p>
            <h3 className="mt-8 text-lg font-bold text-[#0f172a]">本文（要点）</h3>
            <ul className="mt-4 max-w-prose space-y-2 text-left text-base leading-[1.7] text-[#0f172a]">
              <li>良かった行動を、動詞で書く（例：確認／減速／待つ）</li>
              <li>その行動が成立した条件を一言添える（例：雨天／逆光／混雑）</li>
              <li>次週は「同じ条件で再現できたか」を確認する</li>
            </ul>
            <p className="mt-8 border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base font-semibold text-[#0f766e]">
              明日の朝礼で使う一言：「良かった点は、行動と条件のセットで残す。」
            </p>
            <p className="mt-4 text-sm text-[#57534e]">タグ：評価／振り返り／記録</p>
          </article>
        </div>
      </section>

      <section className={`${sectionPad} border-b-0 bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            社内の安全活動に合わせた講習設計もご相談ください。
          </h2>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
          </div>
        </div>
      </section>
    </>
  );
}
