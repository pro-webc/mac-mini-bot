import GoogleMapEmbed from "@/components/GoogleMapEmbed";
import { Inbox } from "lucide-react";

const MAP_EMBED =
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&hl=ja&z=13&ie=UTF8&iwloc=&output=embed";

export default function TsHubContactMethodsSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Inbox className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div className="min-w-0 flex-1">
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              連絡方法
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              まずは下記のフォームからご連絡ください。電話での受付は、掲載が確定次第、本ページに追記します。
            </p>
            <div className="mt-8">
              <h3 className="text-left text-lg font-semibold text-[#18181B]">
                所在地の目安（鹿児島市）
              </h3>
              <p className="mt-2 text-left text-sm text-[#52525B]">
                正式な住所・営業所が確定したら、地図の表示を差し替えます。
              </p>
              <div className="mt-4">
                <GoogleMapEmbed
                  title="鹿児島市周辺の地図"
                  embedUrl={MAP_EMBED}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
