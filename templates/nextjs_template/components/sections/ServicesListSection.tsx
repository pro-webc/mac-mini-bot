import Link from "next/link";
import { Cable, ChevronRight, Radio, Wrench } from "lucide-react";

const services = [
  {
    id: "mobile_base_station",
    title: "携帯電話基地局関連工事",
    summary:
      "通信設備工事は、設計意図どおりに「つながる」状態へ仕上げるまでが仕事です。現地条件に合わせて段取りを組み、試験・調整まで一貫して支援します。",
    points: [
      "アンテナ・機器の設置、配線、接続作業の支援",
      "既設設備の更新・整備に関する相談",
      "運用開始に向けた試験・調整の支援（範囲は案件により異なります）",
    ],
    icon: Radio,
  },
  {
    id: "etc_lane",
    title: "ETCレーン等の通信設備工事",
    summary:
      "路側設備まわりの設置・接続に関する工事支援を行います。通行への影響や安全確保が鍵となる場面では、関係者との調整と作業手順の明確化を進めます。",
    points: [
      "路側設備まわりの設置・接続に関する工事支援",
      "現場条件に応じた施工手順の提案",
      "関係者との調整が必要な案件の進行支援（一般論）",
    ],
    icon: Wrench,
  },
  {
    id: "maintenance",
    title: "保守・不具合対応の相談",
    summary:
      "障害・不具合に関する復旧支援の可否は、事前ヒアリングのうえで整理します。緊急度の高い案件はまず電話でのご連絡をお願いします。",
    points: [
      "障害状況のヒアリングと復旧方針の整理支援",
      "夜間・休日対応の可否は運用条件を確認のうえで調整",
      "緊急度の高い案件はまず電話でご連絡ください",
    ],
    icon: Cable,
  },
];

export default function ServicesListSection() {
  return (
    <section
      className="overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="services-list-heading"
    >
      <h2
        id="services-list-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        対応領域の概要
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        料金は案件規模・設備種別・工期・現場条件により個別見積もりです。概算だけ知りたい場合も、可能な範囲で整理します。
      </p>
      <ul className="mt-6 flex flex-col gap-4">
        {services.map((svc) => {
          const Icon = svc.icon;
          return (
            <li
              key={svc.id}
              className="flex flex-col gap-4 rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4 md:flex-row md:justify-between"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex items-start gap-3">
                  <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] border border-[#2563eb]/30 bg-[#EFF6FF] text-[#2563eb]">
                    <Icon className="h-5 w-5" aria-hidden />
                  </span>
                  <div>
                    <h3 className="text-lg font-bold text-[#0F172A]">{svc.title}</h3>
                    <p className="mt-2 text-left text-sm leading-relaxed text-[#475569]">
                      {svc.summary}
                    </p>
                    <ul className="mt-3 list-inside list-disc text-sm text-[#64748B]">
                      {svc.points.map((p) => (
                        <li key={p}>{p}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
              <div className="flex flex-col justify-end gap-2 md:items-end">
                <Link
                  href="/contact"
                  className="inline-flex min-h-[44px] items-center gap-1 text-sm font-semibold text-[#2563eb] hover:text-[#1d4ed8] active:text-[#1e40af] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                >
                  この内容で相談する
                  <ChevronRight className="h-4 w-4" aria-hidden />
                </Link>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
