import Link from "next/link";
import { ChevronRight, Radio, Route, Wrench } from "lucide-react";

const domains = [
  {
    title: "携帯電話基地局関連工事",
    body: "アンテナ・機器の設置、配線、接続作業の支援。既設設備の更新・整備や、運用開始に向けた試験・調整の支援（範囲は案件により異なります）。",
    icon: Radio,
  },
  {
    title: "ETCレーン等の通信設備工事",
    body: "路側設備まわりの設置・接続に関する工事支援。現場条件に応じた施工手順の提案、関係者との調整が必要な案件の進行支援（一般論）。",
    icon: Route,
  },
  {
    title: "保守・不具合対応の相談",
    body: "障害状況のヒアリングと復旧方針の整理支援。夜間・休日対応の可否は運用条件を確認のうえで調整。緊急度の高い案件はまず電話でご連絡ください。",
    icon: Wrench,
  },
];

export default function HomeServiceTeaserSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/20 bg-[#1d4ed8] p-6 md:p-10"
      aria-labelledby="service-teaser-heading"
    >
      <h2
        id="service-teaser-heading"
        className="text-center text-xl font-bold text-white md:text-left md:text-2xl"
      >
        サービス・工事内容（要点）
      </h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-base leading-relaxed text-[#BFDBFE] md:mx-0 md:text-left">
        基地局／ETC等の通信設備に関わる設置・接続・整備を中心に支援します。詳細はサービスページで工程と留意点をご確認ください。
      </p>
      <ul className="mt-8 grid gap-4 md:grid-cols-3">
        {domains.map((item) => {
          const Icon = item.icon;
          return (
            <li
              key={item.title}
              className="flex min-h-[220px] flex-col justify-between gap-3 rounded-[12px] border border-white/20 bg-[#2563eb] p-4"
            >
              <div>
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#caeb25]/50 bg-[#1e40af] text-[#caeb25]">
                  <Icon className="h-5 w-5" aria-hidden />
                </span>
                <h3 className="mt-3 text-lg font-bold text-white">{item.title}</h3>
                <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">{item.body}</p>
              </div>
            </li>
          );
        })}
      </ul>
      <div className="mt-8 flex justify-center md:justify-start">
        <Link
          href="/services"
          className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-full bg-[#caeb25] px-6 py-3 text-base font-semibold text-[#0F172A] transition-colors hover:bg-[#b5cf1f] active:bg-[#9fb81a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
        >
          サービス・工事内容を見る
          <ChevronRight className="h-5 w-5" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
