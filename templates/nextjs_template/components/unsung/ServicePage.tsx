import { Check } from "lucide-react";
import Link from "next/link";

import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { secondaryOutlineClass } from "@/lib/ctaButtonClass";

import PageHeaderWithVisual from "./PageHeaderWithVisual";

const sectionY = "py-16 md:py-24";

export default function ServicePage() {
  return (
    <>
      <PageHeaderWithVisual
        title="サービス／メソッド"
        lead="個人の価値観を明確化し、主体的に行動できる人材を育てるためのトレーニングです。知識注入型ではなく、現場の文脈に根ざした言語化と実践へ落とし込みます。"
        visualDescription="エディトリアル横長。ホワイトボードではなく静かな対話の机、資料は最小限。リーダー層の内省と言語化の空気感。ダークトーンに馴染む低コントラストの撮影。"
        visualOverlay="サービス／メソッド"
        aspectClassName="aspect-[4/3] md:aspect-[21/9]"
      />

      <section className={sectionY} aria-labelledby="svc-value-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="svc-value-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            個人の幸福の追求が、企業成長を後押しする
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            個人の幸せと企業成長が同じ軸に乗ったとき、推進力は加速します。方向性を示すだけでは難しい時代に、人材変容の場を組織内に育てる支援を行います。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="svc-method-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="svc-method-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            往復で「本当の思い」を抽出する
          </h2>
          <p className="mt-4 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            メソッドの骨格（コア⇄ロール⇄具体）は、次の三層を行き来しながら進めます。
          </p>

          <div className="mt-10 grid gap-6 lg:grid-cols-3">
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <h3 className="text-lg font-semibold text-[#eceff4]">
                コア（軸）
              </h3>
              <p className="mt-3 text-sm leading-[1.7] text-[#94a3b8]">
                譲れない価値観、判断の根拠になる内側の基準。
              </p>
            </div>
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <h3 className="text-lg font-semibold text-[#eceff4]">
                ロール（ペルソナ）
              </h3>
              <p className="mt-3 text-sm leading-[1.7] text-[#94a3b8]">
                職務・場面で求められる振る舞いと期待のレイヤー。
              </p>
            </div>
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <h3 className="text-lg font-semibold text-[#eceff4]">
                具体の現場
              </h3>
              <p className="mt-3 text-sm leading-[1.7] text-[#94a3b8]">
                会議、評価、日々の意思決定に現れる言動と成果。
              </p>
            </div>
          </div>

          <p className="mt-8 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            この三つを行き来しながら、無意識のペルソナの裏にあるコアの強さに気づき、言動の源泉をクリアにします。
          </p>

          <div className="mt-10">
            <ImagePlaceholder
              description="縦横比 16:9。コア・ロール・具体の三層を示す抽象的ダイアグラム用の余白。中央に往復矢印、周囲に短いラベル領域。写真ではなく図解置き場としてのニュートラル枠。"
              aspectClassName="aspect-video"
            />
          </div>

          <div
            className="mt-10 overflow-x-auto rounded-[14px] border border-[#334155] bg-[#111827] p-6 md:p-8"
            aria-label="コア・ロール・具体の往復（図解）"
          >
            <div className="mx-auto min-w-[280px] max-w-2xl">
              <div className="flex flex-col items-center gap-4 md:flex-row md:items-stretch md:justify-between md:gap-6">
                <div className="w-full rounded-[12px] border border-[#334155] px-4 py-4 text-center md:w-1/3">
                  <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                    コア
                  </p>
                  <p className="mt-2 text-sm text-[#eceff4]">価値観・基準</p>
                </div>
                <div
                  className="hidden items-center text-[#94a3b8] md:flex"
                  aria-hidden
                >
                  ⇄
                </div>
                <div className="w-full rounded-[12px] border border-[#334155] px-4 py-4 text-center md:w-1/3">
                  <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                    ロール
                  </p>
                  <p className="mt-2 text-sm text-[#eceff4]">期待・振る舞い</p>
                </div>
                <div
                  className="hidden items-center text-[#94a3b8] md:flex"
                  aria-hidden
                >
                  ⇄
                </div>
                <div className="w-full rounded-[12px] border border-[#334155] px-4 py-4 text-center md:w-1/3">
                  <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                    具体
                  </p>
                  <p className="mt-2 text-sm text-[#eceff4]">会議・評価・現場</p>
                </div>
              </div>
              <p className="mt-6 text-center text-sm text-[#94a3b8]">
                往復を重ねて、言語化の解像度を上げる
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="svc-why-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="svc-why-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            理解より先に、自分の言葉で語れる状態へ
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            フレームワークの暗記だけでは、場面が変わると再現が難しくなります。だから、本人の文脈に沿って言語化し、翌日からの一歩に自信が持てるところまで伴走します。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="svc-change-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="svc-change-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            こんな変化を目指します
          </h2>
          <ul className="mt-6 max-w-prose space-y-4 text-base leading-[1.7] text-[#94a3b8]">
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>
                評価の揺れに飲まれず、判断軸を自分の言葉で説明できる
              </span>
            </li>
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>役割演技の重なりを整理し、意図的にロールを選べる</span>
            </li>
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>
                会議と業務の設計が変わり、意思決定に時間と集中が戻る
              </span>
            </li>
          </ul>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="svc-audience-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="svc-audience-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            こんな組織・ポジション向け
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            中堅企業から大企業のリーダー層全般。とくに従業員規模がおおむね1,000名前後の企業で、次世代幹部・リーダーの意思決定とエンゲージメントを同時に整えたい場合に適しています。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-t border-[#334155]`}
        aria-labelledby="svc-cta-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="rounded-[14px] border border-[#334155] bg-[#1f2937] p-8 md:p-12">
            <h2
              id="svc-cta-heading"
              className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
            >
              進め方と期間感を確認する
            </h2>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <CtaButton href="/contact">お問い合わせ</CtaButton>
              <Link
                href="/program"
                className={`${secondaryOutlineClass()} inline-flex justify-center sm:justify-start`}
              >
                プログラム概要を見る
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
