import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import LinePlaceholderLink from "@/components/LinePlaceholderLink";

import PageHeaderWithVisual from "./PageHeaderWithVisual";

const sectionY = "py-16 md:py-24";

export default function PricingPage() {
  return (
    <>
      <PageHeaderWithVisual
        title="料金・プラン"
        lead="プログラム構成により変動します。最終見積りはヒアリング後にご提示します。"
        visualDescription="横長。料金表の横に置く説明用の余白。数字は載せず、透明性と見積プロセスの信頼感を伝えるミニマルな構図。ダーク背景に淡いラインアート想定。"
        visualOverlay="料金・透明性"
        aspectClassName="aspect-[4/3] md:aspect-[21/9]"
      />

      <section className={sectionY} aria-labelledby="pricing-table-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="pricing-table-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            プラン一覧
          </h2>
          <p className="mt-4 max-w-prose text-sm leading-[1.7] text-[#94a3b8]">
            お一人あたりの目安（税抜または税込は見積時に明記）
          </p>
          <div className="mt-8 overflow-x-auto rounded-[14px] border border-[#334155]">
            <table className="w-full min-w-[640px] border-collapse text-left text-sm">
              <thead className="bg-[#1f2937]">
                <tr>
                  <th
                    scope="col"
                    className="border-b border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    プログラム
                  </th>
                  <th
                    scope="col"
                    className="border-b border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    お一人あたりの目安
                  </th>
                  <th
                    scope="col"
                    className="border-b border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    備考
                  </th>
                </tr>
              </thead>
              <tbody className="text-[#94a3b8]">
                <tr className="bg-[#111827]">
                  <td className="border-b border-[#334155] px-4 py-4 md:px-6">
                    次世代経営幹部メンバー向けトレーニング
                  </td>
                  <td className="border-b border-[#334155] px-4 py-4 text-[#eceff4] md:px-6">
                    70万〜100万円
                  </td>
                  <td className="border-b border-[#334155] px-4 py-4 md:px-6">
                    構成により変動
                  </td>
                </tr>
                <tr className="bg-[#111827]">
                  <td className="border-b border-[#334155] px-4 py-4 md:px-6">
                    リーダー層向けトレーニング
                  </td>
                  <td className="border-b border-[#334155] px-4 py-4 text-[#eceff4] md:px-6">
                    50万〜80万円
                  </td>
                  <td className="border-b border-[#334155] px-4 py-4 md:px-6">
                    構成により変動
                  </td>
                </tr>
                <tr className="bg-[#111827]">
                  <td className="px-4 py-4 md:px-6">
                    次世代リーダー向けトレーニング（30代〜40代前半）
                  </td>
                  <td className="px-4 py-4 text-[#eceff4] md:px-6">
                    30万円〜
                  </td>
                  <td className="px-4 py-4 md:px-6">
                    上限はプログラムにより変動
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="mt-10">
            <ImagePlaceholder
              description="16:9。見積りの内訳（項目の積み上げ）を示す図解用の余白。テキストは後から入れる前提で、枠とラベル領域のみ。"
              aspectClassName="aspect-video"
            />
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="pricing-includes-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="pricing-includes-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            お見積りに含める項目の例
          </h2>
          <ul className="mt-6 max-w-prose list-disc space-y-2 pl-5 text-base leading-[1.7] text-[#94a3b8]">
            <li>事前ヒアリング</li>
            <li>カリキュラム設計</li>
            <li>ワークショップ</li>
            <li>個別フィードバック</li>
            <li>実践課題</li>
            <li>振り返りセッション（案件により増減）</li>
          </ul>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="pricing-format-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="pricing-format-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            全国・オンライン
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            拠点を問わず実施可能です。運用ルールや情報セキュリティ要件がある場合は初回ヒアリングで確認します。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="pricing-note-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="pricing-note-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            ご留意ください
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            表示金額は目安であり、要件定義の結果により変更があります。契約条件・成果指標は書面で確定します。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-t border-[#334155]`}
        aria-labelledby="pricing-cta-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="rounded-[14px] border border-[#334155] bg-[#1f2937] p-8 md:p-12">
            <h2
              id="pricing-cta-heading"
              className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
            >
              まずは要件をお聞かせください
            </h2>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <CtaButton href="/contact">お問い合わせフォーム</CtaButton>
              <LinePlaceholderLink className="justify-center sm:justify-start">
                LINEで連絡チャネルを追加
              </LinePlaceholderLink>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
