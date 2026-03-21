import GoogleMapEmbed from "@/components/GoogleMapEmbed";
import LinePlaceholderLink from "@/components/LinePlaceholderLink";

import ContactFormSection from "./ContactFormSection";
import PageHeaderWithVisual from "./PageHeaderWithVisual";

const MAP_EMBED =
  "https://maps.google.com/maps?q=%E6%9D%B1%E4%BA%AC%E9%83%BD%E5%A2%A8%E7%94%B0%E5%8C%BA%E6%B1%9F%E6%9D%B1%E6%A9%8B4-27-14+%E6%A5%BD%E5%A4%A9%E5%9C%B0%E3%83%93%E3%83%AB&output=embed&hl=ja";

const sectionY = "py-16 md:py-24";

export default function ContactPage() {
  return (
    <>
      <PageHeaderWithVisual
        title="会社概要／お問い合わせ"
        lead="ご相談・取材・協業のお問い合わせはフォームから承ります。メールでの直接連絡も可能です。"
        visualDescription="横長。コーポレート／相談窓口の落ち着いたトーン。オフィス受付ではなく、信頼感のあるミニマルな空間イメージ。人物はシルエットまたは背面。ダーク基調に馴染むコントラスト。"
        visualOverlay="お問い合わせ・会社概要"
        aspectClassName="aspect-[4/3] md:aspect-[21/9]"
      />

      <section className={sectionY} aria-labelledby="contact-company-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="contact-company-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            会社概要
          </h2>
          <div className="mt-8 overflow-x-auto rounded-[14px] border border-[#334155]">
            <table className="w-full min-w-[280px] border-collapse text-left text-sm">
              <tbody className="text-[#94a3b8]">
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="w-[140px] shrink-0 border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    会社名
                  </th>
                  <td className="px-4 py-4 md:px-6">unsung hero株式会社</td>
                </tr>
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    代表者
                  </th>
                  <td className="px-4 py-4 md:px-6">志田洋二</td>
                </tr>
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    所在地
                  </th>
                  <td className="px-4 py-4 md:px-6">
                    〒130-0022 東京都墨田区江東橋4-27-14 楽天地ビル3F
                  </td>
                </tr>
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    メール
                  </th>
                  <td className="px-4 py-4 md:px-6">
                    <a
                      href="mailto:yoji.shida@us-hero.com"
                      className="text-[#eceff4] underline-offset-4 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
                    >
                      yoji.shida@us-hero.com
                    </a>
                  </td>
                </tr>
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    設立
                  </th>
                  <td className="px-4 py-4 md:px-6">
                    法人設立に向けた手続きを進めており、確定情報は順次本ページで更新します
                  </td>
                </tr>
                <tr className="border-b border-[#334155] bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    電話
                  </th>
                  <td className="px-4 py-4 md:px-6">
                    サイトでは公開しておりません（ご用件はメールまたはフォームでお願いいたします）
                  </td>
                </tr>
                <tr className="bg-[#111827]">
                  <th
                    scope="row"
                    className="border-r border-[#334155] px-4 py-4 font-semibold text-[#eceff4] md:px-6"
                  >
                    営業時間
                  </th>
                  <td className="px-4 py-4 md:px-6">
                    サイトでは掲載しておりません
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="contact-map-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="contact-map-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            地図
          </h2>
          <p className="mt-4 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            Googleマップの埋め込みで所在地を表示します（実装で設置）。
          </p>
          <div className="mt-8 overflow-hidden rounded-[14px] border border-[#334155]">
            <GoogleMapEmbed
              embedUrl={MAP_EMBED}
              title="unsung hero株式会社 所在地（東京都墨田区江東橋）"
              wrapperClassName="max-h-none md:aspect-[21/9]"
            />
          </div>
        </div>
      </section>

      <ContactFormSection />

      <section className={sectionY} aria-labelledby="contact-line-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="contact-line-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            LINEでつながる
          </h2>
          <p className="mt-4 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            最新情報や短いTipsをお届けします。URLが整い次第、ボタンから友だち追加いただけます。
          </p>
          <div className="mt-6">
            <LinePlaceholderLink>LINEで友だち追加（URL設定後に有効化）</LinePlaceholderLink>
          </div>
        </div>
      </section>

      <section
        id="privacy"
        className={`${sectionY} border-t border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="privacy-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="privacy-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            プライバシーポリシー
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            お預かりした個人情報は、お問い合わせ対応・ご提案・契約手続きのために利用し、目的外利用や第三者提供は法令に基づく場合を除き行いません。保管期間・開示等の請求手続きについては、お問い合わせフォームからご連絡ください。
          </p>
        </div>
      </section>
    </>
  );
}
