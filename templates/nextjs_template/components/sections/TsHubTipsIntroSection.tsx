import { Lightbulb } from "lucide-react";

export default function TsHubTipsIntroSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FAFAF9] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
          <div>
            <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
              使い方の提案
            </h2>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              冒頭で今日のテーマを一言で示し、本文は短く、最後に確認質問を一つ添えると定着しやすいです。担当者が読み上げやすい文量を意識しています。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
