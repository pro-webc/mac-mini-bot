export default function TshContactPageHeaderSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="contact-page-h1"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h1
          id="contact-page-h1"
          className="text-3xl font-bold text-[#1c1917] md:text-4xl"
        >
          お問い合わせ・相談予約
        </h1>
        <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          2営業日以内にご返信いたします（繁忙期は前後する場合があります）。
        </p>
      </div>
    </section>
  );
}
