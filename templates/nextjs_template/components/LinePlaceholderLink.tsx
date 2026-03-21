"use client";

import { SiLine } from "react-icons/si";

import { secondaryOutlineClass } from "@/lib/ctaButtonClass";

type LinePlaceholderLinkProps = {
  children: React.ReactNode;
  className?: string;
};

/** LINE公式URLは後から設定。クリックは無効化し、見た目のみ CTA 帯に揃える。 */
export default function LinePlaceholderLink({
  children,
  className = "",
}: LinePlaceholderLinkProps) {
  return (
    <a
      href="#"
      onClick={(e) => e.preventDefault()}
      className={`${secondaryOutlineClass()} ${className}`.trim()}
      aria-disabled="true"
    >
      <span className="inline-flex items-center gap-2">
        <SiLine className="h-5 w-5 shrink-0 text-[#06C755]" aria-hidden />
        <span>{children}</span>
      </span>
    </a>
  );
}
