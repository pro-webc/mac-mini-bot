export default function WorksFilterSection() {
  const tags = ["すべて", "水まわり（仮）", "内装（仮）", "外構（仮）"];

  return (
    <section className="bg-[#FFFFFF] px-4 py-10 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-lg font-semibold text-[#0F172A]">
          絞り込み（将来拡張用の静的タグ）
        </h2>
        <p className="mt-2 text-left text-sm text-[#475569]">
          初期リリースでは表示のみです。タグ体系が決まり次第、インタラクションを接続します。
        </p>
        <ul className="mt-6 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <li key={tag}>
              <button
                type="button"
                className="rounded-full border border-[#E2E8F0] bg-[#F8FAFC] px-4 py-2 text-sm font-medium text-[#475569] hover:border-[#0EA5E9] hover:bg-[#E0F2FE] hover:text-[#0369A1] active:border-[#0284C7] active:bg-[#BAE6FD] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7] disabled:cursor-not-allowed disabled:bg-[#94A3B8] disabled:text-white"
                disabled={tag !== "すべて"}
              >
                {tag}
              </button>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-left text-xs text-[#475569]">
          「すべて」以外は disabled 表示のデモです。有効化時は hover / active の配色を維持します。
        </p>
      </div>
    </section>
  );
}
