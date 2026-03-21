export default function TshFaqPageHeaderSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="faq-page-h1"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h1
          id="faq-page-h1"
          className="text-3xl font-bold text-[#1c1917] md:text-4xl"
        >
          よくあるご質問
        </h1>
        <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          相談前に多いご質問を整理しました。個別の条件によって答えが変わる項目は、お問い合わせで補足します。
        </p>
      </div>
    </section>
  );
}
