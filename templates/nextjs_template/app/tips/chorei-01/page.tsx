import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function Chorei01Page() {
  return (
    <div className="w-full">
      <article>
        <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-[#0f172a] md:text-3xl">
                  出発前30秒、後方確認は「見た」ではなく「抜けた」まで
                </h1>
                <div className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                  <p>
                    バックは「見た」で終わると、死角の物体や歩行者を取りこぼしやすいです。朝礼では、次の一文から始めてみてください。「バックは、必ず停止してから、肩越しとミラーで“抜けた”を確認してから動く」。
                  </p>
                  <p className="mt-4">
                    現場では、車種ごとに死角が違うため、「この車はここが見えにくい」を一人ひとり言語化する時間を短く取ると定着しやすいです。
                  </p>
                </div>
                <div className="mt-10">
                  <CtaButton href="/contact">
                    この内容を社内で形にする相談
                  </CtaButton>
                </div>
              </div>
              <div className="w-full max-w-full">
                <ImagePlaceholder
                  aspectClassName="aspect-video"
                  description="16:9。バック開始前の後方確認の手順を示す図解的イメージ（実写ではなく線と矢印）。社用車のミラーと肩越しの視線方向。"
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
