import { Check } from "lucide-react";
import Link from "next/link";

import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { secondaryOutlineClass } from "@/lib/ctaButtonClass";

import PageHeaderWithVisual from "./PageHeaderWithVisual";

const sectionY = "py-16 md:py-24";

export default function WorksPage() {
  return (
    <>
      <PageHeaderWithVisual
        title="実績・事例"
        lead="おおむね10年の個人事業としての経験と高評価を土台に、法人として全国・オンラインで支援を拡張しています。数値の詳細は公開できる範囲で都度ご共有します。"
        visualDescription="横長。事例紹介用のエディトリアル余白。IT企業の会議室というより「変化の前後」を想起させる静かなポートレート領域。顔はボカす／シルエット想定の構図指示。"
        visualOverlay="実績・事例"
        aspectClassName="aspect-[4/3] md:aspect-[21/9]"
      />

      <section className={sectionY} aria-labelledby="works-policy-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="works-policy-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            信頼に必要な事実は、過不足なく
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            具体的な社名の公開が難しい案件には配慮し、業種・規模・課題の型で価値をお伝えします。公開可能な範囲は事例として整理してご紹介します。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="works-case-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="works-case-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            相対評価から、自分の軸での判断へ
          </h2>
          <p className="mt-4 text-sm font-medium text-[#94a3b8]">
            事例：大手IT企業／次世代経営メンバー向けトレーニング
          </p>
          <ul className="mt-6 max-w-prose space-y-4 text-base leading-[1.7] text-[#94a3b8]">
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>相対評価から絶対評価への意識変革と実践</span>
            </li>
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>自己信頼の重要性の理解</span>
            </li>
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>
                持ち帰り業務の大幅な減少と、決める会議への変容
              </span>
            </li>
            <li className="flex gap-3">
              <Check
                className="mt-1 h-5 w-5 shrink-0 text-[#eceff4]"
                aria-hidden
              />
              <span>
                トレーニング開始以降、エンゲージメント係数の大幅な改善・向上
              </span>
            </li>
          </ul>
          <div className="mt-10">
            <ImagePlaceholder
              description="4:3。ファシリテーション後のホワイトボードではなく、成果の変化を示すグラフ置き場（後工程で生成）用の余白。落ち着いたダークUIに馴染むグレー基調。"
              aspectClassName="aspect-[4/3]"
              overlayText="変化の可視化（数値は個別共有）"
            />
          </div>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="works-voice-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="works-voice-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            参加者の変化
          </h2>
          <blockquote className="mt-6 max-w-prose border-l-2 border-[#eceff4] pl-6 text-base leading-[1.7] text-[#eceff4]">
            これまで自分と向き合う時間が十分ではなく、とても新鮮でした。演じている自分の奥にあるコア領域に初めて気づき、言動の源泉がクリアになったことで、明日からの一歩に自信が持てました。ペルソナは無意識にやっていたと思っていましたが、その裏にコアが強くあったことに衝撃を受け、これからの方向性を認識できました。
          </blockquote>
          <p className="mt-4 text-xs text-[#94a3b8]">個人名は非掲載</p>
        </div>
      </section>

      <section
        className={`${sectionY} border-t border-[#334155]`}
        aria-labelledby="works-cta-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="rounded-[14px] border border-[#334155] bg-[#1f2937] p-8 md:p-12">
            <h2
              id="works-cta-heading"
              className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
            >
              貴社の文脈での設計を一緒に考えます
            </h2>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <CtaButton href="/contact">お問い合わせ</CtaButton>
              <Link
                href="/pricing"
                className={`${secondaryOutlineClass()} inline-flex justify-center sm:justify-start`}
              >
                料金レンジを確認
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
