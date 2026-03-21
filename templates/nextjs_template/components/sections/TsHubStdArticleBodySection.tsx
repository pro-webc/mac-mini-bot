import type { TipsArticleBlock } from "@/lib/tipsArticleContent";

type Props = { blocks: TipsArticleBlock[] };

export default function TsHubStdArticleBodySection({ blocks }: Props) {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-label="記事本文"
    >
      <div className="mx-auto max-w-3xl space-y-12 px-4 md:px-6">
        {blocks.map((block, i) => {
          if (block.type === "h2_bullets") {
            return (
              <div key={`${block.h2}-${i}`}>
                <h2 className="border-b border-[#E2E8F0] pb-3 text-xl font-semibold text-[#0F172A] md:text-2xl">
                  {block.h2}
                </h2>
                <ul className="mt-6 flex flex-col gap-3">
                  {block.bullets.map((b) => (
                    <li
                      key={b}
                      className="border-l-4 border-[#14B8A6] pl-4 text-left text-base leading-[1.7] text-[#0F172A]"
                    >
                      {b}
                    </li>
                  ))}
                </ul>
              </div>
            );
          }
          return (
            <div key={`${block.h2}-${i}`}>
              <h2 className="border-b border-[#E2E8F0] pb-3 text-xl font-semibold text-[#0F172A] md:text-2xl">
                {block.h2}
              </h2>
              <blockquote className="mt-6 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 text-left text-base italic leading-[1.7] text-[#0F172A]">
                {block.quote}
              </blockquote>
            </div>
          );
        })}
      </div>
    </section>
  );
}
