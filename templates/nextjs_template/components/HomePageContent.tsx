import Link from "next/link";
import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function HomePageContent() {
  return (
    <>
      <section
        className={`${sectionPad} bg-[#ffffff]`}
        aria-labelledby="home-hero-heading"
      >
        <div className={inner}>
          <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
            <div>
              <h1
                id="home-hero-heading"
                className="text-balance text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl"
              >
                <span className="block">
                  現場の運転を、朝礼で使える「短い知恵」に。
                </span>
                <span className="mt-3 block text-xl font-bold text-[#0f766e] sm:text-2xl md:text-3xl">
                  説教で終わらない、企業向け交通安全教育。
                </span>
              </h1>
              <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
                鹿児島市エリアを主な活動範囲とし、白ナンバーで車両を複数台お持ちの事業者さま向けに、講習・伴走型の安全運転意識づけを提供しています。机上の話だけでなく、対話と可視化、一般道路での走行を前提とした評価の視点までをセットで設計し、安全運転管理者・運行管理担当者の方が「業務の合間に振り返れる」形でお届けします。
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
                <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
                <CtaButton href="/contact">まずは相談する</CtaButton>
              </div>
              <p className="mt-6 text-sm leading-[1.7] text-[#57534e]">
                講習の全体像は
                <Link
                  href="/program"
                  className="mx-1 font-medium text-[#0f766e] underline-offset-2 hover:text-[#115e59] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
                >
                  講習プログラム
                </Link>
                、進め方の考え方は
                <Link
                  href="/service"
                  className="mx-1 font-medium text-[#0f766e] underline-offset-2 hover:text-[#115e59] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
                >
                  サービス・強み
                </Link>
                をご覧ください。
              </p>
            </div>
            <div>
              <ImagePlaceholder
                aspectClassName="aspect-[4/3]"
                overlayText="現場の対話と振り返りが続く様子"
                description="横長・企業の朝礼またはミーティング室。ホワイトボード前で少人数が円卓的に座り、講師ではなく参加者同士の視線が交わる構図。自然光、落ち着いたティールのアクセント小物、書類より会話が主役の雰囲気。"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            こんな場面で選ばれています
          </h2>
          <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-[1.7] text-[#0f172a]">
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              朝礼やミーティングで、毎回同じ注意喚起になりがち
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              事故の後追いではなく、日常の運転行動を「見える化」したい
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              講習を受けても、現場の会話が続かない
            </li>
            <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
              社内で安全運転の共通言語が育ちにくい
            </li>
          </ul>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            机上で終わらせないために、3つをセットで組み立てます。
          </h2>
          <div className="mt-10 grid gap-8 md:grid-cols-3">
            <div className="flex flex-col border border-[#e7e5e4] bg-[#fafaf9] p-6">
              <h3 className="text-lg font-bold text-[#0f172a]">
                コーチング型の進行
              </h3>
              <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                同じ説明の繰り返しに寄せず、参加者同士の気づきがつながる問いかけと振り返りを中心に進行します。
              </p>
            </div>
            <div className="flex flex-col border border-[#e7e5e4] bg-[#fafaf9] p-6">
              <h3 className="text-lg font-bold text-[#0f172a]">
                可視化（機材・手順を含む設計）
              </h3>
              <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                「聞いたつもり」で終わらないよう、理解が揃うための見せ方・進行設計を重視します（機材の詳細はお打ち合わせで調整）。
              </p>
            </div>
            <div className="flex flex-col border border-[#e7e5e4] bg-[#fafaf9] p-6">
              <h3 className="text-lg font-bold text-[#0f172a]">
                一般道路での走行を前提とした評価の視点
              </h3>
              <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                GPS等によるスコア化や改善ポイントの整理など、事前の見える化に資する評価の考え方を、現場運用に合わせてご提案します。
              </p>
            </div>
          </div>
          <p className="mt-8 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            効果を数値で断定する表現は避け、仕組みと運用の両面から「何が変わりやすいか」を一緒に整理します。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <div className="grid gap-10 lg:grid-cols-2 lg:items-start">
            <div>
              <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
                まずはこんな企業さまからご相談いただいています。
              </h2>
              <ul className="mt-8 space-y-4 text-left text-base leading-[1.7] text-[#0f172a]">
                <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
                  白ナンバーの事業用車を複数台お持ちの企業（目安としておおむね20台以上の保有規模を想定した設計からご相談可能）
                </li>
                <li className="border border-[#e7e5e4] bg-[#ffffff] p-4">
                  安全運転管理者・運行管理担当者の方が、社内の安全活動の核になっている組織
                </li>
              </ul>
              <p className="mt-6 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
                運輸（緑ナンバー）領域は、現フェーズの主戦場とは別枠で将来的に拡張可能です。まずは現状の運用と課題を伺い、無理のない範囲から設計します。
              </p>
            </div>
            <div>
              <ImagePlaceholder
                aspectClassName="aspect-video"
                description="複数台の白ナンバー社用車が駐車した事業所前のイメージ。人物は小さめ、車両台数と運用の規模感が伝わる構図。晴天・清潔感、過度な演出なし。"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            導入までの流れ（概要）
          </h2>
          <ol className="mt-8 max-w-prose list-decimal space-y-3 pl-5 text-left text-base leading-[1.7] text-[#0f172a]">
            <li>面談予約またはお問い合わせ</li>
            <li>現状把握のオンライン面談（外部予約ツール）</li>
            <li>実施形態・回数・内容のすり合わせ</li>
            <li>ご提案・お見積り</li>
            <li>実施・フォロー（必要に応じて）</li>
          </ol>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
            <CtaButton href="/contact">お問い合わせへ</CtaButton>
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            朝礼で使える「一口アドバイス」
          </h2>
          <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            短時間で読めるネタを週次で積み上げます。最新記事は一覧ページへ。
          </p>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            <article className="flex flex-col justify-between border border-[#e7e5e4] bg-[#ffffff] p-6">
              <div>
                <h3 className="text-lg font-bold text-[#0f172a]">
                  朝礼1分：ハンドル操作の前に「視線の順番」を決める
                </h3>
                <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                  急な操作は視線移動が先に崩れがち。短い合言葉で揃えます。
                </p>
                <p className="mt-4 text-xs text-[#57534e]">2026/03/17</p>
                <p className="mt-1 text-xs font-medium text-[#0f766e]">
                  朝礼／視線
                </p>
              </div>
            </article>
            <article className="flex flex-col justify-between border border-[#e7e5e4] bg-[#ffffff] p-6">
              <div>
                <h3 className="text-lg font-bold text-[#0f172a]">
                  管理者向け：注意喚起が「同じ話」になるときの切り口
                </h3>
                <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                  ルールの再掲だけに寄せず、現場の判断軸を一つ足す方法。
                </p>
                <p className="mt-4 text-xs text-[#57534e]">2026/03/10</p>
                <p className="mt-1 text-xs font-medium text-[#0f766e]">
                  管理者／対話
                </p>
              </div>
            </article>
            <article className="flex flex-col justify-between border border-[#e7e5e4] bg-[#ffffff] p-6">
              <div>
                <h3 className="text-lg font-bold text-[#0f172a]">
                  評価メモの残し方：良い運転の「再現条件」を一言で
                </h3>
                <p className="mt-3 text-left text-sm leading-[1.7] text-[#57534e]">
                  褒めるポイントを行動に落とすと、次週の振り返りが速くなります。
                </p>
                <p className="mt-4 text-xs text-[#57534e]">2026/03/03</p>
                <p className="mt-1 text-xs font-medium text-[#0f766e]">
                  評価／振り返り
                </p>
              </div>
            </article>
          </div>
          <div className="mt-10">
            <CtaButton href="/column">コラム一覧へ</CtaButton>
          </div>
        </div>
      </section>

      <section
        className={`${sectionPad} border-b-0 bg-[#ffffff]`}
        aria-labelledby="home-final-cta"
      >
        <div className={inner}>
          <h2
            id="home-final-cta"
            className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl"
          >
            次の一手は、短い面談からで大丈夫です。
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            課題の整理、実施形態の候補、社内説明に使える言い回しまで、必要な範囲でお手伝いします。
          </p>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
            <CtaButton href="/contact">お問い合わせ</CtaButton>
          </div>
        </div>
      </section>
    </>
  );
}
