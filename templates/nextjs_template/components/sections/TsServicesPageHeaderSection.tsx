export default function TsServicesPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="services-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="services-h1"
          className="text-left text-2xl font-bold text-[#18181B] md:text-3xl"
        >
          サービス・講習の内容
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>企業向け交通安全教育／セミナー・講習の提供</p>
          <p>担当者向けから始め、社内展開しやすい設計を志向</p>
        </div>
      </div>
    </section>
  );
}
