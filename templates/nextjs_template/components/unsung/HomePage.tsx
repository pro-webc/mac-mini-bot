import {
  ArrowLeftRight,
  CircleDot,
  Layers,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import LinePlaceholderLink from "@/components/LinePlaceholderLink";
import { secondaryOutlineClass } from "@/lib/ctaButtonClass";

const sectionY = "py-16 md:py-24";

export default function HomePage() {
  return (
    <>
      <section
        className={`${sectionY} border-b border-[#334155]`}
        aria-labelledby="home-hero-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-14">
            <div>
              <p className="inline-flex items-center gap-2 text-sm font-medium tracking-wide text-[#94a3b8]">
                <Sparkles className="h-4 w-4 text-[#eceff4]" aria-hidden />
                人材トレーニング
              </p>
              <h1
                id="home-hero-heading"
                className="mt-4 text-3xl font-semibold leading-tight tracking-tight text-[#eceff4] sm:text-4xl md:text-[2.75rem] md:leading-tight"
              >
                評価に寄りかからず、意思で動くリーダーへ。
              </h1>
              <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
                知識を詰め込む研修ではなく、一人ひとりの価値観（コア）と役割（ロール／ペルソナ）を往復しながら言語化し、主体的な行動へつなげる人材トレーニングです。中堅〜大企業のリーダー層、とくに従業員規模がおおむね1,000名前後の組織での実装を想定しています。
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
                <CtaButton href="/contact">お問い合わせはこちら</CtaButton>
                <LinePlaceholderLink className="justify-center sm:justify-start">
                  LINEで情報を受け取る
                </LinePlaceholderLink>
              </div>
            </div>
            <div>
              <ImagePlaceholder
                description="横長ワイド。落ち着いたダークトーンのオフィスまたはファシリテーション空間。中堅〜大企業のリーダー層が対話する様子のシルエット。余白多め・エディトリアルな静けさ。"
                aspectClassName="aspect-[4/3] lg:aspect-video"
                overlayText="意思で動くリーダーシップ"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="home-pain-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="home-pain-heading"
            className="max-w-prose text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            結果は出ているのに、自分の意志が置き去りになっていないか。
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            伝統的な評価基準に寄り添いすぎると、自己の軸が定まりにくくなります。日本人の強みである「慮る力」が、最適化の動きへつながり、思いとは別のペルソナを無意識に重ねてしまうこともあります。結果至上主義の圧に押し流され、役割はこなせても納得感が残らない——その違和感は、個人だけの問題ではなく、組織の持続的な推進力にも影響します。
          </p>
          <div className="mt-10 max-w-5xl">
            <ImagePlaceholder
              description="横長ワイド。評価面談や会議のテーブル越しの緊張と静けさ。数字の資料ではなく「納得感」の余白を想起させる構図。ダークトーン・低コントラスト。"
              aspectClassName="aspect-video"
            />
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="home-core-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="home-core-heading"
            className="max-w-prose text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            コアとペルソナをつなぎ直し、意思決定の質を上げる。
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            コアだけを孤立して作り込むのは難しい。だからこそ、ロール（ペルソナ）を手がかりに、具体と抽象を何度も往復します。演じたいロールの奥にある譲れない価値観を見つけ、企業が目指す方向性と、個人の幸福が同じ軸上に乗る形を一緒に設計します。
          </p>
          <div className="mt-10 grid gap-4 rounded-[14px] border border-[#334155] bg-[#111827] p-6 md:grid-cols-3 md:p-8">
            <div className="flex gap-3">
              <CircleDot
                className="mt-0.5 h-6 w-6 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <div>
                <p className="text-sm font-semibold text-[#eceff4]">往復</p>
                <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                  抽象（コア）と具体（現場）を行き来し、言語の解像度を上げます。
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Layers
                className="mt-0.5 h-6 w-6 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <div>
                <p className="text-sm font-semibold text-[#eceff4]">
                  ロールを手がかりに
                </p>
                <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                  期待される振る舞いのレイヤーから、譲れない価値観へ遡行します。
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <ArrowLeftRight
                className="mt-0.5 h-6 w-6 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <div>
                <p className="text-sm font-semibold text-[#eceff4]">
                  意思決定の質
                </p>
                <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                  個人の納得と、組織の方向性を同じ軸に載せる設計を支援します。
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="home-works-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="home-works-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            現場で起きた変化の輪郭
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            大手IT企業向けの次世代経営メンバー向けトレーニングでは、相対評価から絶対評への意識転換、自己信頼の理解、持ち帰り業務の削減と意思決定会議への変容、エンゲージメント係数の大幅な改善・向上などが見られました。詳細は実績ページをご覧ください。
          </p>
          <div className="mt-10 max-w-5xl">
            <ImagePlaceholder
              description="横長ワイド。研修後のチームがホワイトボード前で対話する様子のシルエット。成果の数字より「対話の質」が伝わるエディトリアル写真想定。ダーク基調。"
              aspectClassName="aspect-video"
            />
          </div>
          <div className="mt-8">
            <Link
              href="/works"
              className={`${secondaryOutlineClass()} inline-flex`}
            >
              実績・事例を見る
            </Link>
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="home-pricing-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="home-pricing-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            まずはレンジで全体像を把握
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            プログラム構成により変動します。具体的な設計はヒアリングのうえでご提案します。
          </p>
          <div className="mt-8">
            <Link
              href="/pricing"
              className={`${secondaryOutlineClass()} inline-flex`}
            >
              料金・プランを見る
            </Link>
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-t border-[#334155]`}
        aria-labelledby="home-final-cta-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="rounded-[14px] border border-[#334155] bg-[#1f2937] p-8 md:p-12">
            <h2
              id="home-final-cta-heading"
              className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
            >
              まずは状況をお聞かせください
            </h2>
            <p className="mt-4 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
              全国・オンラインで対応しています。ご相談内容に応じて、最適な進め方をご案内します。
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <CtaButton href="/contact">お問い合わせフォームへ</CtaButton>
              <LinePlaceholderLink className="justify-center sm:justify-start">
                LINEでつながる
              </LinePlaceholderLink>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
