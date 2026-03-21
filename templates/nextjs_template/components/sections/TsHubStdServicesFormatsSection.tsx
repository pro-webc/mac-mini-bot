import { Video, Users, Phone, LineChart } from "lucide-react";

const items = [
  { text: "事前ヒアリング（オンライン可）", Icon: Video },
  { text: "集合研修・ワークショップ", Icon: Users },
  { text: "フォロー面談（オンライン可）", Icon: Phone },
  { text: "必要に応じて評価セッションを組み込む", Icon: LineChart },
];

export default function TsHubStdServicesFormatsSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="formats-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="formats-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          実施形態（例）
        </h2>
        <ul className="mt-10 grid gap-4 sm:grid-cols-2">
          {items.map((item) => (
            <li
              key={item.text}
              className="flex items-start gap-3 rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-5"
            >
              <item.Icon className="h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
              <span className="text-left text-base text-[#0F172A]">{item.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
