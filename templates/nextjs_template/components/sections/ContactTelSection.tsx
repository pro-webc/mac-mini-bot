import { Phone } from "lucide-react";

export default function ContactTelSection() {
  return (
    <section className="bg-[#FFFFFF] px-4 py-12 md:px-6">
      <div className="mx-auto max-w-2xl rounded-[20px] border border-[#E2E8F0] p-8">
        <h2 className="flex items-center gap-2 text-xl font-bold text-[#0F172A]">
          <Phone className="h-6 w-6 text-[#0284C7]" aria-hidden />
          電話でのお問い合わせ
        </h2>
        <a
          href="tel:0471227322"
          className="mt-4 inline-block text-2xl font-bold text-[#0369A1] hover:text-[#075985] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
        >
          0471-22-7322
        </a>
        <p className="mt-2 text-left text-sm text-[#475569]">
          暫定表記です。受付時間・休業日は確定後に更新します。
        </p>
      </div>
    </section>
  );
}
