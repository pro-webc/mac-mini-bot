import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";

import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";

import "./globals.css";

const noto = Noto_Sans_JP({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://example.com"),
  title: {
    default: "unsung hero株式会社 | コアとロールをつなぐ人材トレーニング",
    template: "%s | unsung hero株式会社",
  },
  description:
    "評価に寄りかからず、意思で動くリーダーへ。中堅〜大企業のリーダー層向けに、価値観と役割を往復しながら言語化し、主体的な行動へつなげるトレーニングを全国・オンラインで提供します。",
  openGraph: {
    title: "unsung hero株式会社 | コアとロールをつなぐ人材トレーニング",
    description:
      "知識注入型ではなく、現場の文脈に根ざした言語化と実践。次世代幹部・リーダーの意思決定とエンゲージメントを整えます。",
    type: "website",
    locale: "ja_JP",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className={noto.variable}>
      <body
        className={`${noto.className} min-h-dvh overflow-x-hidden bg-[#111827] text-base leading-[1.7] text-[#eceff4] antialiased`}
      >
        <SiteHeader />
        <main className="min-h-[50vh] w-full">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
