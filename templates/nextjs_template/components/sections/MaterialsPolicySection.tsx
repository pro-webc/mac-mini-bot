import { AlertTriangle, HardHat, Scale } from "lucide-react";

export default function MaterialsPolicySection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="materials-policy-heading"
    >
      <h2
        id="materials-policy-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        安全・法令順守・現場ルール
      </h2>
      <p className="mt-4 text-left text-base leading-relaxed text-[#475569]">
        高所作業や交通規制エリアでの作業など、リスクの性質は案件ごとに異なります。関係法令・現場ルールを踏まえ、手順と相互確認を重ねることを基本とします。夜間・休日対応は案件により個別調整となり、断定は避けます。
      </p>
      <ul className="mt-8 grid gap-4 md:grid-cols-3">
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <HardHat className="h-8 w-8 text-[#2563eb]" aria-hidden />
          <p className="text-base font-semibold text-[#0F172A]">安全運用</p>
          <p className="text-left text-sm leading-relaxed text-[#475569]">
            保護具・立入管理・作業手順の確認を、チームで徹底します（詳細は案件ごと）。
          </p>
        </li>
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <Scale className="h-8 w-8 text-[#2563eb]" aria-hidden />
          <p className="text-base font-semibold text-[#0F172A]">法令・ルールの尊重</p>
          <p className="text-left text-sm leading-relaxed text-[#475569]">
            許認可や関係者調整が必要な場面では、事前共有と合意形成を優先します。
          </p>
        </li>
        <li className="flex flex-col gap-2 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <AlertTriangle className="h-8 w-8 text-[#2563eb]" aria-hidden />
          <p className="text-base font-semibold text-[#0F172A]">夜間・休日の扱い</p>
          <p className="text-left text-sm leading-relaxed text-[#475569]">
            現場ルール・許可・協力体制により異なります。要件を伺い、可否と手順を整理します。
          </p>
        </li>
      </ul>
    </section>
  );
}
