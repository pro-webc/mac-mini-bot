import { MessageCircle, BarChart3 } from "lucide-react";

export default function TsHubStdHomeValueBridgeSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="value-bridge-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="value-bridge-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          なぜ「話し合い」と「見える化」が必要なのか
        </h2>
        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <div className="rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6">
            <p className="max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
              交通安全の話は、正しいことを並べるほど現場に戻りにくくなることがあります。TS-hubでは、ルールの暗記ではなく、日々の運行で再現できる判断と習慣を、対話を通じて言語化します。
            </p>
            <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
              評価は、個人をさらすためではなく、チームで改善点を共有するための材料として扱います。
            </p>
          </div>
          <ul className="flex flex-col gap-4">
            <li className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-4">
              <MessageCircle
                className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]"
                aria-hidden
              />
              <p className="text-left text-base leading-[1.7] text-[#0F172A]">
                <span className="font-semibold text-[#0F172A]">
                  講義だけで終わらせない：
                </span>
                参加者の経験から「自社ならではの落とし穴」を抽出する
              </p>
            </li>
            <li className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-4">
              <BarChart3
                className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]"
                aria-hidden
              />
              <p className="text-left text-base leading-[1.7] text-[#0F172A]">
                <span className="font-semibold text-[#0F172A]">
                  見える化は目的ではない：
                </span>
                安全会議や現場指示に使える形へ整える
              </p>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
