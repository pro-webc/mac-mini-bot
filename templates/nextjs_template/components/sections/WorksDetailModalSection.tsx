const details = [
  {
    id: "p1",
    title: "浴室まわりのメンテナンス（仮）",
    body: "依頼背景、採用した方針、注意した近隣対応などを段落で記載する予定です。確定文案はクライアント確認後に差し替えます。",
  },
  {
    id: "p2",
    title: "キッチン周辺の調整（仮）",
    body: "使用部材や工期の目安、お客様の声（掲載許諾が取れた場合）をここに展開します。",
  },
  {
    id: "p3",
    title: "外構・排水まわり（仮）",
    body: "天候による日程変更の記録や、完了後のメンテナンス提案などを載せる想定です。",
  },
];

export default function WorksDetailModalSection() {
  return (
    <section className="bg-[#FFFFFF] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          詳細（同一ページ内アコーディオン）
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          6 ページ構成のまま、モーダルの代わりに軽量な折りたたみで補足文を表示します。
        </p>
        <div className="mt-8 space-y-3">
          {details.map((d) => (
            <details
              key={d.id}
              className="group rounded-[16px] border border-[#E2E8F0] bg-[#F8FAFC] p-4 open:bg-[#FFFFFF]"
            >
              <summary className="cursor-pointer text-base font-semibold text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]">
                {d.title}
              </summary>
              <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
                {d.body}
              </p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
