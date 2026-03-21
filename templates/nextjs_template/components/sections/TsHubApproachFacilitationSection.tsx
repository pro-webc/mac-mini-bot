import ImagePlaceholder from "@/components/ImagePlaceholder";
import { MessagesSquare } from "lucide-react";

const bullets = [
  "心理的安全性はスローガンではなく、進行で作るものです。",
  "批判ではなく観察と仮説に寄せることで、本音の情報が集まりやすくなります。",
];

export default function TsHubApproachFacilitationSection() {
  return (
    <section className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="grid items-start gap-10 lg:grid-cols-2">
          <div>
            <div className="flex items-start gap-3">
              <MessagesSquare
                className="h-8 w-8 shrink-0 text-[#1D4ED8]"
                aria-hidden
              />
              <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
                対話の設計：聞かせるだけにしない
              </h2>
            </div>
            <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#52525B] md:text-base">
              安全な対話ルールを先に置き、小グループで整理し、全体共有の型へつなぎます。
            </p>
            <h3 className="mt-8 text-left text-lg font-semibold text-[#18181B]">
              対話のルールを先に置く理由
            </h3>
            <ul className="mt-4 space-y-3">
              {bullets.map((t) => (
                <li
                  key={t}
                  className="border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-left text-sm leading-relaxed text-[#18181B] md:text-base"
                >
                  {t}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <ImagePlaceholder
              description="円卓または長机で少人数が対話しているイラスト風（線は柔らかく、彩度低め）。吹き出しは空でも可。威圧感のない配色。"
              aspectClassName="aspect-video"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
