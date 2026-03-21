export default function TshContactPrivacySection() {
  return (
    <section
      id="privacy_compact"
      className="scroll-mt-[calc(10vh+1rem)] border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="privacy-compact-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
        <h2
          id="privacy-compact-heading"
          className="text-lg font-semibold text-[#1c1917]"
        >
          個人情報の取扱い（簡易）
        </h2>
        <p className="mt-3 max-w-prose text-left text-sm leading-relaxed text-[#57534e]">
          お預かりした情報は、お問い合わせ対応とご提案のために利用し、目的外利用はしません。第三者提供は法令に基づく場合を除き行いません。保管期間は対応完了から合理的な期間とし、後日削除します。
        </p>
      </div>
    </section>
  );
}
