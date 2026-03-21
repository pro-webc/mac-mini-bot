import type { Metadata } from "next";
import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";
import "./globals.css";

const siteTitle =
  "現場の運転を朝礼で使える短い知恵に｜鹿児島の法人向け交通安全教育";
const siteDescription =
  "鹿児島市エリアを主な活動範囲とし、白ナンバーで車両を複数台お持ちの事業者向けに、講習・伴走型の安全運転意識づけを提供しています。対話と可視化、一般道路での走行を前提とした評価の視点までをセットで設計します。";

const siteJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "ProfessionalService",
      name: "法人向け交通安全教育",
      description: siteDescription,
      areaServed: "鹿児島市および周辺の法人",
    },
    {
      "@type": "WebSite",
      name: "法人向け交通安全教育",
      description: siteDescription,
    },
  ],
};

export const metadata: Metadata = {
  metadataBase: new URL("https://example.com"),
  title: {
    default: siteTitle,
    template: `%s｜法人向け交通安全教育`,
  },
  description: siteDescription,
  openGraph: {
    title: siteTitle,
    description: siteDescription,
    locale: "ja_JP",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="min-h-dvh bg-[#fafaf9] font-sans text-base leading-[1.7] text-[#0f172a] antialiased">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(siteJsonLd) }}
        />
        <SiteHeader />
        <main className="w-full min-h-[60vh] overflow-x-hidden px-0 pb-16 pt-[calc(10vh+1rem)] md:pt-28">
          {children}
        </main>
        <SiteFooter />
      </body>
    </html>
  );
}
