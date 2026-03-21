"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";

import CtaButton from "@/components/CtaButton";
import LinePlaceholderLink from "@/components/LinePlaceholderLink";

const nav = [
  { href: "/", label: "ホーム" },
  { href: "/service", label: "サービス" },
  { href: "/program", label: "プログラム" },
  { href: "/works", label: "実績" },
  { href: "/pricing", label: "料金" },
  { href: "/contact", label: "お問い合わせ" },
] as const;

export default function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-[#334155] bg-[#111827]/95 backdrop-blur-sm motion-reduce:backdrop-blur-none">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 md:px-6">
        <Link
          href="/"
          className="min-h-[44px] min-w-[44px] shrink-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
        >
          <span className="block max-w-[200px] text-sm font-semibold leading-tight tracking-wide text-[#eceff4] md:max-w-none md:text-base">
            unsung hero株式会社
          </span>
        </Link>

        <nav
          aria-label="メイン"
          className="hidden items-center gap-1 md:flex md:gap-2 lg:gap-4"
        >
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="whitespace-nowrap rounded-[10px] px-2 py-2 text-sm font-medium tracking-wide text-[#eceff4] hover:text-[#ffffff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4] lg:px-3 lg:text-[15px]"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <LinePlaceholderLink>LINEで最新情報を受け取る</LinePlaceholderLink>
          <CtaButton href="/contact">お問い合わせ</CtaButton>
        </div>

        <button
          type="button"
          className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-[10px] border border-[#334155] text-[#eceff4] hover:bg-[#1f2937] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4] md:hidden"
          aria-expanded={open}
          aria-controls="mobile-nav"
          aria-label={open ? "メニューを閉じる" : "メニューを開く"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {open ? (
        <div
          id="mobile-nav"
          className="border-t border-[#334155] bg-[#111827] px-4 py-4 md:hidden"
        >
          <nav aria-label="モバイルメイン" className="flex flex-col gap-1">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="min-h-[44px] whitespace-nowrap rounded-[10px] px-3 py-3 text-base font-medium tracking-wide text-[#eceff4] hover:bg-[#1f2937]"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="mt-4 flex flex-col gap-3">
              <LinePlaceholderLink className="w-full justify-center">
                LINEで最新情報を受け取る
              </LinePlaceholderLink>
              <CtaButton href="/contact" className="w-full justify-center">
                お問い合わせ
              </CtaButton>
            </div>
          </nav>
        </div>
      ) : null}
    </header>
  );
}
