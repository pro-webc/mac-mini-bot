import TsHubStdArticleBodySection from "@/components/sections/TsHubStdArticleBodySection";
import TsHubStdArticleFooterSection from "@/components/sections/TsHubStdArticleFooterSection";
import TsHubStdArticleHeaderSection from "@/components/sections/TsHubStdArticleHeaderSection";
import {
  tipsArticleSlugs,
  tipsArticles,
} from "@/lib/tipsArticleContent";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

type Props = { params: { slug: string } };

export function generateStaticParams() {
  return tipsArticleSlugs.map((slug) => ({ slug }));
}

export function generateMetadata({ params }: Props): Metadata {
  const article = tipsArticles[params.slug];
  if (!article) return { title: "記事" };
  return {
    title: article.h1,
    description: article.intro.slice(0, 120),
  };
}

export default function TipsArticlePage({ params }: Props) {
  const article = tipsArticles[params.slug];
  if (!article) notFound();

  return (
    <>
      <TsHubStdArticleHeaderSection h1={article.h1} intro={article.intro} />
      <TsHubStdArticleBodySection blocks={article.blocks} />
      <TsHubStdArticleFooterSection
        h2={article.footerH2}
        body={article.footerBody}
        secondaryCtaLabel={article.secondaryCtaLabel}
      />
    </>
  );
}
