import Link from "next/link";

const footerNav = [
  { href: "/", label: "ホーム" },
  { href: "/service", label: "サービス・強み" },
  { href: "/program", label: "講習プログラム" },
  { href: "/column", label: "お役立ちコラム" },
  { href: "/about", label: "講師・事業について" },
  { href: "/contact", label: "お問い合わせ・相談予約" },
];

export default function SiteFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-[#e7e5e4] bg-[#fafaf9]">
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <div className="grid gap-10 md:grid-cols-2">
          <div>
            <Link
              href="/"
              className="text-left text-base font-bold text-[#0f172a] hover:text-[#0f766e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            >
              法人向け交通安全教育
            </Link>
            <p className="mt-3 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
              白ナンバーで車両を複数台お持ちの事業者さま向けに、講習・伴走型の安全運転意識づけを提供しています。
            </p>
            <p className="mt-4 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
              鹿児島市エリアを中心に、企業向けの交通安全教育を提供しています。
            </p>
          </div>
          <nav aria-label="フッターナビゲーション">
            <p className="text-left text-xs font-semibold uppercase tracking-wide text-[#57534e]">
              サイトマップ
            </p>
            <ul className="mt-3 flex flex-col gap-2">
              {footerNav.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="inline-flex min-h-[44px] items-center text-sm font-medium text-[#0f766e] hover:text-[#115e59] active:text-[#134e4a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
        <p className="mt-10 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
          お問い合わせフォームで取得する情報は、ご相談内容の確認・連絡、および講習の準備のために利用し、目的の範囲を超えて第三者に提供することはありません。
        </p>
        <p className="mt-6 text-center text-sm text-[#57534e]">
          © {year} 交通安全教育サービス運営
        </p>
      </div>
    </footer>
  );
}
