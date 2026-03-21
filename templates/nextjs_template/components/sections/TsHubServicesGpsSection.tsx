import ImagePlaceholder from "@/components/ImagePlaceholder";
import { Gauge } from "lucide-react";

export default function TsHubServicesGpsSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#F4F4F5] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="grid items-start gap-10 lg:grid-cols-2">
          <div>
            <div className="flex items-start gap-3">
              <Gauge className="h-8 w-8 shrink-0 text-[#1D4ED8]" aria-hidden />
              <h2 className="text-left text-xl font-bold tracking-tight text-[#18181B] md:text-2xl">
                一般道路コースでの評価・フィードバック（GPS等）
              </h2>
            </div>
            <p className="mt-5 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              感覚的な上手い下手ではなく、改善点の優先順位を話し合える材料をそろえます。コース条件、車両、記録方法、本人同意の取り方は、必ず事前にすり合わせます。
            </p>
            <p className="mt-4 max-w-prose border border-[#E4E4E7] bg-[#FFFFFF] p-4 text-left text-sm leading-relaxed text-[#52525B]">
              安全運転や事故防止を保証するものではありません。支援は教育・運用改善の補助です。
            </p>
          </div>
          <div>
            <ImagePlaceholder
              description="車内ではなく、タブレットに走行レビュー画面が映り、講師と担当者が横並びで画面を見ながら会話しているクローズアップ。画面内容は抽象化。柔らかいトーン、反射が強すぎない。"
              aspectClassName="aspect-[4/3]"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
