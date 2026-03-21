export default function TshProgramPageHeaderSection() {
  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#ffffff]"
      aria-labelledby="program-page-h1"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h1
          id="program-page-h1"
          className="text-3xl font-bold text-[#1c1917] md:text-4xl"
        >
          プログラムと実施イメージ
        </h1>
        <p className="mt-5 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          以下は代表的な実施イメージです。車両台数、拠点、業種、既存の教育体制に合わせて組み替えます。
        </p>
      </div>
    </section>
  );
}
