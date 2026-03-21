export default function TsHubStdContactHeroSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-14 md:py-16"
      aria-labelledby="contact-hero-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="contact-hero-heading"
          className="text-3xl font-bold leading-tight text-[#0F172A] md:text-4xl"
        >
          お問い合わせ・無料相談
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.7] text-[#0F172A]">
          <p>
            お問い合わせ内容を確認のうえ、営業日以内にご返信します。
          </p>
          <p>
            電話でのご相談を希望の場合は、メッセージ欄に希望時間帯をご記入ください（番号は確定後にサイトへ反映します）。
          </p>
        </div>
      </div>
    </section>
  );
}
