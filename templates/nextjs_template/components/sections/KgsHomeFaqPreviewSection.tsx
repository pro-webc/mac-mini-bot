import Link from "next/link";
import { HelpCircle } from "lucide-react";

const previewFaqs = [
  {
    question: "オンラインでも実施できますか？",
    answer:
      "可能な場合があります。対象者の分散状況、演習の可否、機器の扱いにより最適解が変わるため、まずは現状を伺います。",
  },
  {
    question: "人数に制限はありますか？",
    answer:
      "設計により異なります。少人数からの試行も可能です。まずは想定人数と会場条件（オンライン比率含む）をお知らせください。",
  },
];

const linkClass =
  "inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#1D4ED8] bg-[#FFFFFF] px-6 py-3 text-base font-semibold text-[#1D4ED8] transition-colors hover:border-[#1E40AF] hover:bg-[#F4F4F5] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] motion-safe:transition-colors";

export default function KgsHomeFaqPreviewSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-home-faq-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-home-faq-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          よくある質問（抜粋）
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-relaxed text-[#52525B]">
          オンライン実施の可否、人数、費用の扱い、準備物など（詳細条件は要確認で逃がさない）
        </p>
        <div className="mt-10 space-y-6">
          {previewFaqs.map((f) => (
            <article
              key={f.question}
              className="border border-[#E4E4E7] bg-[#FAFAF9] p-5"
            >
              <h3 className="text-left text-lg font-semibold text-[#18181B]">
                {f.question}
              </h3>
              <p className="mt-3 text-left text-base leading-relaxed text-[#18181B]">
                {f.answer}
              </p>
            </article>
          ))}
        </div>
        <div className="mt-10">
          <Link href="/contact#faq-full" className={`${linkClass} w-full sm:w-auto`}>
            <HelpCircle className="h-5 w-5 shrink-0" aria-hidden />
            FAQをもっと見る
          </Link>
        </div>
      </div>
    </section>
  );
}
