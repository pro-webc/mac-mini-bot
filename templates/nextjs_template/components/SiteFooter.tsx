import Link from "next/link";

const links = [
  { href: "/", label: "ホーム" },
  { href: "/service", label: "サービス" },
  { href: "/program", label: "プログラム" },
  { href: "/works", label: "実績" },
  { href: "/pricing", label: "料金" },
  { href: "/contact", label: "お問い合わせ" },
  { href: "/contact#privacy", label: "プライバシー" },
] as const;

export default function SiteFooter() {
  return (
    <footer className="border-t border-[#334155] bg-[#111827]">
      <div className="mx-auto max-w-6xl px-4 py-14 md:px-6">
        <div className="flex flex-col gap-10 md:flex-row md:justify-between">
          <div>
            <p className="text-lg font-semibold tracking-wide text-[#eceff4]">
              unsung hero株式会社
            </p>
            <p className="mt-3 max-w-prose text-sm leading-[1.7] text-[#94a3b8]">
              〒130-0022 東京都墨田区江東橋4-27-14 楽天地ビル3F
            </p>
            <p className="mt-2 text-sm text-[#94a3b8]">
              <a
                href="mailto:yoji.shida@us-hero.com"
                className="text-[#eceff4] underline-offset-4 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              >
                yoji.shida@us-hero.com
              </a>
            </p>
          </div>
          <nav aria-label="フッター" className="flex flex-col gap-2">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="min-h-[44px] whitespace-nowrap py-2 text-sm font-medium tracking-wide text-[#eceff4] hover:text-[#ffffff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
        <p className="mt-10 border-t border-[#334155] pt-8 text-center text-xs text-[#94a3b8] md:text-left">
          © unsung hero株式会社
        </p>
        <p className="mt-4 text-center text-xs text-[#94a3b8] md:text-left">
          本サイトの内容は予告なく変更される場合があります。
        </p>
      </div>
    </footer>
  );
}
