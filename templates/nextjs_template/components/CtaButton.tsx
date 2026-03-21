"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { ReactNode } from "react";

import { ctaButtonClass } from "@/lib/ctaButtonClass";

type CtaButtonProps = {
  href?: string;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit";
  onClick?: () => void;
};

export default function CtaButton({
  href,
  children,
  className = "",
  disabled,
  type = "button",
  onClick,
}: CtaButtonProps) {
  const cls = `${ctaButtonClass(disabled)} ${className}`.trim();

  const inner = (
    <span className="inline-flex items-center gap-2">
      <span>{children}</span>
      <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
    </span>
  );

  if (href && !disabled) {
    const isExternal = /^https?:\/\//i.test(href);
    if (isExternal) {
      return (
        <a
          href={href}
          className={cls}
          target="_blank"
          rel="noopener noreferrer"
        >
          {inner}
        </a>
      );
    }
    return (
      <Link href={href} className={cls}>
        {inner}
      </Link>
    );
  }

  return (
    <button type={type} className={cls} disabled={disabled} onClick={onClick}>
      {inner}
    </button>
  );
}
