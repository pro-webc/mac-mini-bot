import { AlertTriangle } from "lucide-react";

export default function KgsSvcLimitationsSection() {
  const items = [
    "鹿児島市周辺を主対象。遠方はオンライン中心など要相談",
    "大型案件の同時多発は受けられない場合がある",
    "外部予約・フォームの役割分担は運用確定後に最適化",
  ];

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-svc-limits-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-svc-limits-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          対応範囲と制約（正直さ）
        </h2>
        <ul className="mt-8 max-w-prose space-y-4 text-left text-base leading-relaxed text-[#18181B]">
          {items.map((t) => (
            <li key={t} className="flex gap-3">
              <AlertTriangle
                className="mt-0.5 h-5 w-5 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
