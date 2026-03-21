import Link from "next/link";
import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function TipsIndexPage() {
  return (
    <div className="w-full">
      <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-[#0f172a] md:text-4xl">
                朝礼ひとこと
              </h1>
              <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                週1回の更新を想定した短いメモです。朝礼でそのまま読める長さを基本にします。
              </p>
            </div>
            <div className="w-full max-w-full">
              <ImagePlaceholder
                aspectClassName="aspect-[4/3]"
                overlayText="朝礼で読み上げる短いメモのイメージ"
                description="4:3。会議室の朝礼、手元の短いメモカード。時計は視界の端。落ち着いた室内光。"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionY} bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <ul className="grid gap-6 md:grid-cols-3">
            {[
              {
                title:
                  "出発前30秒、後方確認は「見た」ではなく「抜けた」まで",
                lead: "バック開始の手順を言葉にして、抜け漏れを減らす話題出し。",
                href: "/tips/chorei-01",
              },
              {
                title: "左折のとき、二段階確認が空振りになる典型",
                lead: "速度と位置取りがずれると「確認したつもり」が起きる、という短い整理。",
                href: "/tips/chorei-02",
              },
              {
                title: "社用車の共有ルールが曖昧だと、事故が個人に寄りやすい",
                lead: "管理者が朝礼で言える、最小ルールの切り出し方。",
                href: "/tips/chorei-03",
              },
            ].map((item) => (
              <li key={item.href}>
                <article className="flex h-full flex-col justify-between border border-[#e7e5e4] bg-[#ffffff] p-6">
                  <div>
                    <h2 className="text-lg font-semibold text-[#0f172a]">
                      {item.title}
                    </h2>
                    <p className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                      {item.lead}
                    </p>
                  </div>
                  <Link
                    href={item.href}
                    className="mt-6 inline-flex min-h-[44px] items-center font-semibold text-[#0f766e] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
                  >
                    続きを読む
                  </Link>
                </article>
              </li>
            ))}
          </ul>
          <div className="mt-12 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>相談予約</CtaButton>
            <CtaButton href="/contact">講習の相談</CtaButton>
          </div>
        </div>
      </section>
    </div>
  );
}
