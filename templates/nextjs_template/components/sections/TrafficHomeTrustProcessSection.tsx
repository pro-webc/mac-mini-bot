import { ClipboardCheck, MessageCircle, MonitorPlay, RefreshCw } from "lucide-react";

const steps = [
  {
    title: "事前ヒアリング",
    body: "目的・参加者・車両運用の論点を整理",
    Icon: MessageCircle,
  },
  {
    title: "実施計画のすり合わせ",
    body: "時間・場・進行をすり合わせ",
    Icon: ClipboardCheck,
  },
  {
    title: "当日の運営",
    body: "ワークと評価の見せ方をセットで運営",
    Icon: MonitorPlay,
  },
  {
    title: "振り返り",
    body: "次の打ち手を言語化（社内展開のたたき台）",
    Icon: RefreshCw,
  },
];

export default function TrafficHomeTrustProcessSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-trust-process-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-trust-process-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          進行イメージ（導入〜振り返り）
        </h2>
        <p className="mt-4 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          一人運営のため、同時多発の大型案件表現は避け、相談ベースで現実的な範囲をすり合わせます。見積・実施条件はお問い合わせ後に個別提示します。
        </p>
        <ol className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {steps.map(({ title, body, Icon }, idx) => (
            <li
              key={title}
              className="relative rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5"
            >
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] text-sm font-semibold text-[#0F766E]">
                  {idx + 1}
                </span>
                <Icon className="h-6 w-6 text-[#0F766E]" aria-hidden />
              </div>
              <h3 className="mt-3 text-left text-lg font-semibold leading-[1.45] text-[#18181B]">
                {title}
              </h3>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#52525B]">
                {body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
