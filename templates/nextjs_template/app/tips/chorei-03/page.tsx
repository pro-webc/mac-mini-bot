import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function Chorei03Page() {
  return (
    <div className="w-full">
      <article>
        <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-[#0f172a] md:text-3xl">
                  社用車の「共有ルール」が曖昧だと事故が個人に寄る
                </h1>
                <div className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                  <p>
                    社用車は複数人が乗り換えるほど、「この車の癖」や「返却時の確認」が曖昧になります。朝礼では、ルールを増やしすぎず、まず3つに絞るのがおすすめです。例：返却時の周囲確認、タイヤ外傷の見る位置、キーと書類の受け渡し。
                  </p>
                  <p className="mt-4">
                    ルールが短いほど、管理者の説明も現場も同じ言葉で揃いやすいです。
                  </p>
                </div>
                <div className="mt-10">
                  <CtaButton href="/contact">
                    社内ルール整備を一緒に整理
                  </CtaButton>
                </div>
              </div>
              <div className="w-full max-w-full">
                <ImagePlaceholder
                  aspectClassName="aspect-video"
                  description="16:9。社用車のキーとチェックリストが並ぶデスク。共有ルール3項目が箇条書きされたカードのイメージ。"
                />
              </div>
            </div>
          </div>
        </section>
        <section className={`${sectionY} bg-[#fafaf9]`}>
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <CtaButton href={BOOKING_URL}>相談予約</CtaButton>
          </div>
        </section>
      </article>
    </div>
  );
}
