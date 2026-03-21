import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function Chorei02Page() {
  return (
    <div className="w-full">
      <article>
        <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-[#0f172a] md:text-3xl">
                  左折のとき、二段階確認が空振りになる典型
                </h1>
                <div className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                  <p>
                    二段階確認が形だけになるとき、多くは速度が早すぎるか、停止位置が浅いかのどちらかです。朝礼の話題はシンプルで十分です。「左折は、一旦止まってから、再発進が遅くてもいい」。
                  </p>
                  <p className="mt-4">
                    “止まる位置”を社内で統一語にすると、指摘が個人攻撃に見えにくくなります。
                  </p>
                </div>
                <div className="mt-10">
                  <CtaButton href="/contact">運転指導の進め方を相談</CtaButton>
                </div>
              </div>
              <div className="w-full max-w-full">
                <ImagePlaceholder
                  aspectClassName="aspect-video"
                  description="16:9。左折待ちの停止位置を俯瞰で示す簡易図。交差点手前のラインと車両の位置関係。"
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
