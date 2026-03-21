import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function ServicePageContent() {
  return (
    <>
      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h1 className="text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl">
            サービス・強み
          </h1>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
            交通安全の研修は「正しさ」より先に、現場に戻れるかが重要です。ここでは、他社講習と並べて比較されやすい論点を、仕組みの違いとして整理します。
          </p>
          <div className="mt-10">
            <ImagePlaceholder
              aspectClassName="aspect-[21/9]"
              overlayText="問いかけと振り返りが中心の進行イメージ"
              description="ワイド・研修室の前席から見た構図。投影では箇条の羅列ではなく、矢印と短いフレーズだけのシンプル図解。講師は横、参加者の後頭部が手前に少し見える。落ち着いた配色（白・ストーン・ティールのアクセント）。"
            />
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            よくある講習との違い
          </h2>
          <div className="mt-8 overflow-x-auto rounded-none border border-[#e7e5e4] bg-[#ffffff]">
            <table className="min-w-[640px] w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-[#e7e5e4] bg-[#fafaf9]">
                  <th className="border-r border-[#e7e5e4] p-4 font-semibold text-[#0f172a]">
                    比較軸
                  </th>
                  <th className="border-r border-[#e7e5e4] p-4 font-semibold text-[#0f172a]">
                    一般的になりがちな形
                  </th>
                  <th className="p-4 font-semibold text-[#0f172a]">
                    当サービスの設計意図
                  </th>
                </tr>
              </thead>
              <tbody className="text-[#0f172a]">
                <tr className="border-b border-[#e7e5e4]">
                  <td className="border-r border-[#e7e5e4] p-4 font-medium">
                    進行
                  </td>
                  <td className="border-r border-[#e7e5e4] p-4 leading-[1.7]">
                    講師の説明が中心
                  </td>
                  <td className="p-4 leading-[1.7]">
                    問いかけと振り返りで、参加者同士の気づきをつなぐ
                  </td>
                </tr>
                <tr className="border-b border-[#e7e5e4]">
                  <td className="border-r border-[#e7e5e4] p-4 font-medium">
                    理解の深さ
                  </td>
                  <td className="border-r border-[#e7e5e4] p-4 leading-[1.7]">
                    資料の理解で完結しがち
                  </td>
                  <td className="p-4 leading-[1.7]">
                    見せ方・手順で「腹落ち」まで寄せる
                  </td>
                </tr>
                <tr className="border-b border-[#e7e5e4]">
                  <td className="border-r border-[#e7e5e4] p-4 font-medium">
                    現場への接続
                  </td>
                  <td className="border-r border-[#e7e5e4] p-4 leading-[1.7]">
                    受講後に個人差が出やすい
                  </td>
                  <td className="p-4 leading-[1.7]">
                    日常の運転行動に戻すための評価視点と改善の切り口をセットで提示
                  </td>
                </tr>
                <tr>
                  <td className="border-r border-[#e7e5e4] p-4 font-medium">
                    管理者の負担
                  </td>
                  <td className="border-r border-[#e7e5e4] p-4 leading-[1.7]">
                    開催報告で終わりやすい
                  </td>
                  <td className="p-4 leading-[1.7]">
                    朝礼や短時間の振り返りに転用しやすい言語化を意識
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-6 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            上表は「設計の意図」を示すための整理であり、他社の良否を断定するものではありません。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            同じ注意の繰り返しから、会話が続く形へ
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            安全運転の話は、正論ほど現場で摩擦が出ます。進行では、結論を先に押し付けず、現場の判断場面に近い問いから入り、短い共有と要約で次の行動に繋げます。
          </p>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              ルールの暗記ではなく、「その場面で何を優先するか」を言語化する
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              失敗談も含めた共有がしやすい進行ルールを最初に合意する
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              管理者向けに、翌週以降の振り返り質問例を渡す
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            理解が揃うまでの道筋を、見える化する
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            説明の正確さだけでなく、参加者の理解が揃うまでのプロセスを設計します。機材や資料の構成は、参加人数・会場条件・オンライン併用の有無に応じて調整します（詳細はお打ち合わせ）。
          </p>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              危険予測のポイントを、場面ごとに分解して見せる
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              体感と言語化を往復させ、社内共有用の短いフレーズに落とす
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              管理者が週次で使える「チェックの問い」をセットでお渡しする
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            一般道路の走行を前提に、改善の糸口を拾い上げる
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            事故後の後追いだけに頼らず、日常の走行から改善余地を見つけるための評価の考え方を扱います。GPS等によるスコア化や改善ポイントの整理は、プライバシーと運用負荷のバランスを最優先に、導入可否と範囲を相談しながら決めます。
          </p>
          <ul className="mt-8 max-w-prose space-y-3 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              「良かった点」と「再現したい条件」をセットで記録する
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              個人攻撃に寄らないフィードバックの型を共有する
            </li>
            <li className="border border-[#e7e5e4] bg-[#fafaf9] p-4">
              管理者が現場に戻しやすい粒度でレポート方針を決める
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} border-b-0 bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            よくあるご質問（サービス理解）
          </h2>
          <dl className="mt-8 space-y-8">
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                社内の雰囲気が硬いのですが、大丈夫ですか？
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                進行は「正しさの押し付け」より、現場の言葉に戻すことを優先します。最初に共有ルールを短く合意し、負担の少ない問いから始めます。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                うちは車両タイプが混在しています。
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                想定外の場面が出やすいほど、共通の判断軸が効きます。保有車両の構成と運用実態を伺い、優先順位を一緒に決めます。
              </dd>
            </div>
          </dl>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href="/program">講習プログラムの詳細へ</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
          </div>
        </div>
      </section>
    </>
  );
}
