import { Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

export default function KgsAboutCtaSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-about-cta-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-about-cta-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          背景まで含めて知りたい方へ
        </h2>
        <p className="mt-6 max-w-prose text-left text-base leading-relaxed text-[#18181B]">
          社内説明用に、進行イメージ資料の共有も可能（範囲は要確認）
        </p>
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            <Send className="h-5 w-5 shrink-0" aria-hidden />
            質問を送る
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
