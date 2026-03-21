export default function TshTipsPageHeaderSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="tips-page-h1"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h1
          id="tips-page-h1"
          className="text-3xl font-bold text-[#1c1917] md:text-4xl"
        >
          お役立ち情報
        </h1>
        <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          よくいただくご質問の背景にもある、「現場で今日から使える短い話題」をまとめています。週次更新を想定し、短く読める分量にしています。
        </p>
      </div>
    </section>
  );
}
