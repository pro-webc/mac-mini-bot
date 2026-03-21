import Link from "next/link";

type Props = { h1: string; intro: string };

export default function TsHubStdArticleHeaderSection({ h1, intro }: Props) {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-14 md:py-16"
      aria-labelledby="article-h1"
    >
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <nav className="text-sm text-[#64748B]" aria-label="パンくず">
          <ol className="flex flex-wrap gap-2">
            <li>
              <Link
                href="/tips"
                className="text-[#0F766E] hover:text-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
              >
                一口アドバイス
              </Link>
            </li>
            <li aria-hidden>/</li>
            <li className="text-[#0F172A]">記事</li>
          </ol>
        </nav>
        <h1
          id="article-h1"
          className="mt-6 text-3xl font-bold leading-tight text-[#0F172A] md:text-4xl"
        >
          {h1}
        </h1>
        <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          {intro}
        </p>
      </div>
    </section>
  );
}
