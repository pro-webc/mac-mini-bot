import { ClipboardCheck, Lock, Sparkles } from "lucide-react";

export default function KgsHomeTrustStripSection() {
  const items = [
    {
      icon: ClipboardCheck,
      text: "実施前に目的・対象・時間設計・オンライン比率を擦り合わせ",
    },
    {
      icon: Lock,
      text: "個人情報・位置情報の扱いは手続きと説明範囲を事前に確認（詳細は契約・運用設計で確定）",
    },
    {
      icon: Sparkles,
      text: "事例・ロゴは許諾取得後に掲載（未提供の間は非掲載またはプレースホルダ方針を明記）",
    },
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-24"
      aria-labelledby="kgs-home-trust-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-trust-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          進め方の透明性
        </h2>
        <ul className="mt-10 grid gap-6 md:grid-cols-3">
          {items.map(({ icon: Icon, text }) => (
            <li
              key={text}
              className="flex gap-4 border border-[#E4E4E7] bg-[#FFFFFF] p-5"
            >
              <Icon
                className="mt-0.5 h-6 w-6 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <p className="text-left text-sm leading-relaxed text-[#18181B]">
                {text}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
