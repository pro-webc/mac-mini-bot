"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowRight, Menu, X } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import { ctaButtonClass } from "@/lib/ctaButtonClass";
import { BOOKING_URL } from "@/lib/bookingUrl";

const nav = [
  { href: "/", label: "ホーム" },
  { href: "/service", label: "サービス・強み" },
  { href: "/program", label: "講習プログラム" },
  { href: "/column", label: "お役立ちコラム" },
  { href: "/about", label: "講師・事業について" },
  { href: "/contact", label: "お問い合わせ・相談予約" },
];

export default function SiteHeader() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const firstFocusRef = useRef<HTMLAnchorElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const close = useCallback(() => setOpen(false), []);

  useEffect(() => {
    if (!open) return;
    firstFocusRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const panel = panelRef.current;
    if (!panel) return;

    const focusable = panel.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );
    const list = Array.from(focusable);

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        close();
        triggerRef.current?.focus();
        return;
      }
      if (e.key !== "Tab" || list.length === 0) return;
      const first = list[0];
      const last = list[list.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, close]);

  const navLinkClass =
    "whitespace-nowrap rounded-[8px] px-2 py-2 text-sm font-medium tracking-wide text-[#ffffff] transition-colors hover:bg-[#115e59] active:bg-[#134e4a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ffffff] lg:px-3";

  const mobileStackClass =
    "inline-flex min-h-[44px] w-full items-center justify-center rounded-[12px] px-4 py-3 text-base font-semibold";

  const secondaryHeaderCta =
    "inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-[12px] border-2 border-[#ffffff] bg-[#fafaf9] px-4 py-2 text-sm font-semibold text-[#0f766e] hover:bg-[#f5f5f4] active:bg-[#e7e5e4] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ffffff] motion-safe:transition-colors";

  return (
    <header className="fixed inset-x-0 top-0 z-50 h-[10vh] min-h-[56px] border-b border-[#e7e5e4] bg-[#0f766e]">
      <div className="mx-auto flex h-full max-w-6xl items-center justify-between gap-2 px-4 md:gap-4 md:px-6">
        <Link
          href="/"
          className="min-w-0 whitespace-nowrap text-xs font-bold tracking-wider text-[#ffffff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ffffff] sm:text-sm md:text-base"
        >
          <span className="block truncate md:inline">
            法人向け交通安全教育
          </span>
        </Link>
        <nav
          className="hidden items-center gap-1 xl:flex"
          aria-label="主なページナビゲーション"
        >
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className={navLinkClass}>
              {item.label}
            </Link>
          ))}
          <CtaButton href={BOOKING_URL} className="ml-1 !min-h-[44px] !px-4 !text-sm">
            面談を予約する
          </CtaButton>
          <Link href="/contact" className={`${secondaryHeaderCta} ml-1`}>
            <span className="inline-flex items-center gap-2">
              お問い合わせ
              <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            </span>
          </Link>
        </nav>
        <div className="flex items-center gap-2 xl:hidden">
          <CtaButton
            href={BOOKING_URL}
            className="!min-h-[44px] !px-3 !py-2 !text-xs sm:!text-sm"
          >
            予約
          </CtaButton>
          <button
            ref={triggerRef}
            type="button"
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-[12px] border border-[#ffffff]/30 bg-[#115e59] text-[#ffffff] hover:bg-[#134e4a] active:bg-[#0d4f4a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ffffff]"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? "メニューを閉じる" : "メニューを開く"}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? (
              <X className="h-6 w-6" aria-hidden />
            ) : (
              <Menu className="h-6 w-6" aria-hidden />
            )}
          </button>
        </div>
      </div>
      {open ? (
        <div
          ref={panelRef}
          id="mobile-nav"
          className="border-t border-[#e7e5e4] bg-[#0f766e] xl:hidden"
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-4">
            <a
              ref={firstFocusRef}
              href={BOOKING_URL}
              target="_blank"
              rel="noopener noreferrer"
              className={`${ctaButtonClass()} ${mobileStackClass}`}
              onClick={close}
            >
              <span className="inline-flex items-center gap-2">
                面談を予約する
                <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
              </span>
            </a>
            <Link
              href="/contact"
              className={`${secondaryHeaderCta} ${mobileStackClass}`}
              onClick={close}
            >
              <span className="inline-flex items-center gap-2">
                お問い合わせ
                <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
              </span>
            </Link>
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="inline-flex min-h-[44px] items-center rounded-[8px] px-3 py-2 text-base font-medium tracking-wide text-[#ffffff] hover:bg-[#115e59] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ffffff]"
                onClick={close}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </header>
  );
}
