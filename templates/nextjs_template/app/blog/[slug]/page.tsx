import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { blogPosts } from "@/lib/blog-posts";

type Props = { params: { slug: string } };

export function generateStaticParams() {
  return blogPosts.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: Props): Metadata {
  const post = blogPosts.find((p) => p.slug === params.slug);
  if (!post) return { title: "記事が見つかりません" };
  return {
    title: post.title,
    description: post.excerpt,
  };
}

export default function BlogArticlePage({ params }: Props) {
  const post = blogPosts.find((p) => p.slug === params.slug);
  if (!post) notFound();

  return (
    <article className="mx-auto max-w-3xl px-4 pb-12 pt-4 md:px-6">
      <p className="text-sm text-[#BFDBFE]">
        <Link
          href="/blog"
          className="font-semibold text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          ブログ一覧へ戻る
        </Link>
      </p>
      <header className="mt-6 border-b border-white/20 pb-6">
        <h1 className="text-2xl font-bold text-white md:text-3xl">{post.title}</h1>
        <p className="mt-2 text-sm text-[#93C5FD]">{post.date}</p>
      </header>
      <div className="mt-8 text-left text-base leading-relaxed text-[#E0E7FF]">
        {post.body.split("\n\n").map((para, i) => (
          <p key={i} className="mb-4">
            {para}
          </p>
        ))}
      </div>
    </article>
  );
}
