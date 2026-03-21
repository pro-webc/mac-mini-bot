import { Shield } from "lucide-react";

export default function TshServiceDataPrivacySection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="data-privacy-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="data-privacy-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          個人情報・走行データの扱い（方針）
        </h2>
        <div className="mt-6 flex gap-4 border border-[#e7e5e4] bg-[#ffffff] p-5">
          <Shield
            className="h-8 w-8 shrink-0 text-[#0f766e]"
            aria-hidden
          />
          <p className="max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
            取得するデータの範囲、保管、廃棄、アクセス権限は、事前に書面または合意内容で明確化します。公開サイト上の一般論に留め、詳細は個別にご確認ください。
          </p>
        </div>
      </div>
    </section>
  );
}
