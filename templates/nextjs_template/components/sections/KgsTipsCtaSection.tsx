import { Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function KgsTipsCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-24"
      aria-labelledby="kgs-tips-cta-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-tips-cta-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          自社の運用に合わせたネタ設計も相談できます
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-relaxed text-[#18181B]">
          業種・走行パターン・事故傾向に合わせた週次テーマの作り方
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            運用相談を送る
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
