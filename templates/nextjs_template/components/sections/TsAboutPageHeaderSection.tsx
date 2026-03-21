export default function TsAboutPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="about-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="about-h1"
          className="text-left text-2xl font-bold text-[#18181B] md:text-3xl"
        >
          事業者について
        </h1>
        <div className="mt-6 max-w-prose space-y-4 text-left text-base leading-[1.75] text-[#18181B]">
          <p>
            交通安全教育・講習を行う一人運営の事業（法人名・屋号・所在地は確定後に掲載）
          </p>
          <p>鹿児島市周辺の企業を主な対象</p>
        </div>
      </div>
    </section>
  );
}
