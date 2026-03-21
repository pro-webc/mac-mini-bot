import { ClipboardList } from "lucide-react";

const checklist = [
  "各事例ごとに、施工前・施工後が分かる写真（最低1組、推奨2組以上）",
  "写り込みがないよう個人情報・番地・車番などを確認済みの素材",
  "事例タイトル（仮称可）と1〜2行の概要文",
  "工期目安、使用部材の希望記載範囲（掲載可否のすり合わせ用）",
  "お客様の声を載せる場合は掲載許諾の記録",
];

export default function WorksClientMaterialSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-6 md:p-10"
      aria-labelledby="works-material-heading"
    >
      <h2
        id="works-material-heading"
        className="inline-flex items-center gap-2 text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        <ClipboardList className="h-7 w-7 text-[#0284C7]" aria-hidden />
        クライアント準備チェックリスト
      </h2>
      <ul className="mt-6 space-y-3 text-left text-sm leading-relaxed text-[#475569]">
        {checklist.map((item) => (
          <li
            key={item}
            className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#F8FAFC] p-3"
          >
            <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-none border border-[#0284C7] bg-[#E0F2FE] text-xs font-bold text-[#0369A1]">
              ✓
            </span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
