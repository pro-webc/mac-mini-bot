import { Mail } from "lucide-react";

export default function TsHubTipsNewsletterSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Mail className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              更新通知について
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              更新通知の配信をご希望の場合は、お問い合わせフォームからお知らせください。運用方法は別途すり合わせます。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
