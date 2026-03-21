import type { Metadata } from "next";
import BlogListSection from "@/components/sections/BlogListSection";
import ContactCtaSection from "@/components/sections/ContactCtaSection";

export const metadata: Metadata = {
  title: "ブログ",
  description:
    "現場メモ、安全と手順、設備の基礎知識など、通信インフラ工事に関する記事一覧（デモ）。",
};

export default function BlogPage() {
  return (
    <>
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <BlogListSection />
      </div>
      <ContactCtaSection variant="blog" />
    </>
  );
}
