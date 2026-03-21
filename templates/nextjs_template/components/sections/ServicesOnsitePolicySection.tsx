import { AlertCircle, Mail } from "lucide-react";
import Link from "next/link";

export default function ServicesOnsitePolicySection() {
  return (
    <section
      id="faq"
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="onsite-heading"
    >
      <h2 id="onsite-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        個人宅訪問の進め方・FAQ
      </h2>
      <div className="mt-6 space-y-4">
        <article className="rounded-none border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <h3 className="flex items-center gap-2 text-base font-bold text-[#0F172A]">
            <AlertCircle className="h-5 w-5 text-[#CA8A04]" aria-hidden />
            訪問前に準備いただきたいこと
          </h3>
          <ul className="mt-2 list-inside list-disc text-sm leading-relaxed text-[#475569]">
            <li>作業場所周辺の物を可能な範囲で移動できる状態にしてください。</li>
            <li>共用部を通る場合は管理規約・近隣への配慮をお願いします。</li>
            <li>安全のため、お子さまやペットの立ち入りにご注意ください。</li>
          </ul>
        </article>
        <article className="rounded-none border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <h3 className="text-base font-bold text-[#0F172A]">連絡について</h3>
          <p className="mt-2 text-left text-sm leading-relaxed text-[#475569]">
            弊社からのご連絡はメールを主とする運用です。お急ぎの場合も、フォームまたはメールにてご記入ください。電話番号は掲載しますが、電話での折り返しを原則としない場合があります。
          </p>
          <Link
            href="/contact"
            className="mt-3 inline-flex min-h-[44px] items-center gap-2 text-sm font-semibold text-[#0369A1] hover:text-[#075985] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
          >
            <Mail className="h-4 w-4" aria-hidden />
            お問い合わせページへ
          </Link>
        </article>
        <div className="rounded-none border border-dashed border-[#CBD5E1] bg-[#FFFFFF] p-4">
          <p className="text-sm font-semibold text-[#0F172A]">よくある質問（仮）</p>
          <dl className="mt-3 space-y-3 text-sm text-[#475569]">
            <div>
              <dt className="font-bold text-[#0F172A]">見積もりは無料ですか？</dt>
              <dd className="mt-1 text-left">
                方針は案件ごとに異なります。確定後、このFAQを更新します。
              </dd>
            </div>
            <div>
              <dt className="font-bold text-[#0F172A]">当日の所要時間は？</dt>
              <dd className="mt-1 text-left">
                作業内容により変動します。訪問前に目安をご連絡します。
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}
