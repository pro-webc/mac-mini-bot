export default function TsContactPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="contact-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="contact-h1"
          className="text-left text-2xl font-bold text-[#18181B] md:text-3xl"
        >
          相談・お問い合わせ
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>3営業日以内に返信（目安。確定後に更新）</p>
          <p>緊急は電話（番号確定後に表示）</p>
        </div>
      </div>
    </section>
  );
}
