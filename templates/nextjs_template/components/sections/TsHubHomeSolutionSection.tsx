import CtaButton from "@/components/CtaButton";
import { MessageCircle, MapPinned, BookOpenCheck } from "lucide-react";

const cards = [
  {
    title: "コーチング型の対話",
    body: "参加者同士が実践を共有し、自社文脈に落とし込みやすい言葉に整えます。ティーチングだけに寄せない進行を重視します。",
    Icon: MessageCircle,
  },
  {
    title: "見える化（GPS等）",
    body: "一般道路のコース走行を前提に、運転の癖や改善点を整理します。良否の根拠が伝わる形を目指します（実施条件は個別に調整）。",
    Icon: MapPinned,
  },
  {
    title: "短いTipsの置き場所",
    body: "週次の短い示唆を積み重ね、担当者がネタに困ったときに戻れるサイトにします。",
    Icon: BookOpenCheck,
  },
];

export default function TsHubHomeSolutionSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
          「腹落ち」までつなぐ3つの柱
        </h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {cards.map(({ title, body, Icon }) => (
            <article
              key={title}
              className="flex flex-col border border-[#E4E4E7] bg-[#FFFFFF] p-5 sm:p-6"
            >
              <Icon className="h-8 w-8 text-[#1D4ED8]" aria-hidden />
              <h3 className="mt-4 text-left text-lg font-semibold text-[#18181B]">
                {title}
              </h3>
              <p className="mt-3 flex-1 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
                {body}
              </p>
            </article>
          ))}
        </div>
        <p className="mt-8 max-w-prose text-left text-sm text-[#52525B]">
          効果は企業環境や運用に左右されます。成果を断定する表現は用いません。
        </p>
        <div className="mt-8">
          <CtaButton href="/services">サービス内容を見る</CtaButton>
        </div>
      </div>
    </section>
  );
}
