import { Mail, MessageCircle, Phone } from "lucide-react";

export default function ContactMethodsSection() {
  return (
    <section
      className="overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="contact-methods-heading"
    >
      <h2
        id="contact-methods-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        連絡方法
      </h2>
      <ul className="mt-6 flex flex-col gap-4">
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#2563eb]/30 bg-[#EFF6FF] text-[#2563eb]">
              <Phone className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-bold text-[#0F172A]">電話</p>
              <p className="text-sm text-[#475569]">
                <a
                  href="tel:0669745788"
                  className="font-semibold text-[#2563eb] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                >
                  06-6974-5788
                </a>
              </p>
              <p className="text-xs text-[#64748B]">9:00〜18:00</p>
            </div>
          </div>
        </li>
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#2563eb]/30 bg-[#EFF6FF] text-[#2563eb]">
              <Mail className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-bold text-[#0F172A]">メール</p>
              <p className="text-sm text-[#475569]">
                <a
                  href="mailto:yy-yumi@task888.com"
                  className="font-semibold text-[#2563eb] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                >
                  yy-yumi@task888.com
                </a>
              </p>
            </div>
          </div>
        </li>
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#2563eb]/30 bg-[#EFF6FF] text-[#06C755]">
              <MessageCircle className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-bold text-[#0F172A]">LINE</p>
              <p className="text-sm leading-relaxed text-[#475569]">
                URL確定後にボタンを設置します。現状は「URL提供後に連携」とだけ明記します。
              </p>
            </div>
          </div>
          <button
            type="button"
            disabled
            className="mt-3 inline-flex min-h-[48px] w-full cursor-not-allowed items-center justify-center rounded-full border-2 border-[#CBD5E1] bg-[#E2E8F0] px-6 py-3 text-base font-semibold text-[#64748B]"
            aria-disabled="true"
          >
            LINEで相談（URL準備中）
          </button>
        </li>
      </ul>
    </section>
  );
}
