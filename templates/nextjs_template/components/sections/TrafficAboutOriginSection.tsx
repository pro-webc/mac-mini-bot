import { Handshake, User } from "lucide-react";

export default function TrafficAboutOriginSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-24"
      aria-labelledby="traffic-origin-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-origin-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          なぜ「言語化」と「見える化」なのか
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <Handshake className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              企業の安全運転管理者コミュニティで聞こえる孤独感とノウハウの分断を起点。
            </p>
          </div>
          <div className="flex gap-4 rounded-sm border border-[#E4E4E7] bg-[#FFFFFF] p-5">
            <User className="h-8 w-8 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-relaxed text-[#18181B]">
              一人事業として、現実的な伴走範囲を明確にする姿勢。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
