export default function WorksDetailPatternSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="works-pattern-heading"
    >
      <h2
        id="works-pattern-heading"
        className="text-xl font-bold text-white md:text-2xl"
      >
        詳細の見せ方
      </h2>
      <p className="mt-3 text-left text-base leading-relaxed text-[#BFDBFE]">
        事例ごとの固定URLは作らず、一覧のカードからモーダルを開いて補足する構成です。長文や追加カットの意図はモーダル内のプレースホルダで示します。
      </p>
      <ol className="mt-6 list-inside list-decimal space-y-2 text-sm leading-relaxed text-[#E0E7FF]">
        <li>一覧で概要と代表画像（プレースホルダ）を提示</li>
        <li>クリックでモーダルを表示し、工程・注意事項の文案を追記可能にする</li>
        <li>実写真は public/images/generated/ へ差し替え</li>
      </ol>
    </section>
  );
}
