export default function CompanyMessageSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="company-message-heading"
    >
      <h2
        id="company-message-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        代表メッセージ
      </h2>
      <p className="mt-2 text-sm font-semibold text-[#caeb25]">代表取締役 米倉 豊</p>
      <div className="mt-4 space-y-4 text-left text-base leading-relaxed text-[#E0E7FF]">
        <p>
          私たちは、人々の生活に欠かせないインフラの現場で、確かなつながりをつくることを仕事にしています。安全とコミュニケーションを両立し、協力会社の皆さまと同じ目線で課題に向き合います。掲載文案は確定稿に差し替えます。
        </p>
        <p className="text-sm text-[#BFDBFE]">
          公式文案は資料取り込み後に確定します。現時点の掲載は一般論とデモ用のたたき台です。
        </p>
      </div>
    </section>
  );
}
