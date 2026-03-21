import CtaButton from "@/components/CtaButton";
import { Check } from "lucide-react";

const positions = [
  {
    title: "通信土木・電気通信工事スタッフ（詳細は随時更新）",
    bullets: [
      "基地局・ネットワーク設備など、現場条件に応じた施工・試験・復旧の支援（範囲は配属により異なります）",
      "図面・手順・相互確認を重ねたうえでの作業を基本とします",
      "全国案件を想定し、移動や宿泊が伴う場合があります（頻度は時期・ポジションにより異なります）",
    ],
  },
  {
    title: "現場サポート・事務連携（要相談）",
    bullets: [
      "書類・スケジュール・関係者連絡と現場支援が交差する役割のイメージです",
      "配属や業務範囲は選考時に個別にご説明します",
      "未経験の可能性がある場合も、前提条件は選考のなかで確認します",
    ],
  },
];

const valueProps = [
  "手に職を伸ばせる：現場の型を身につけながら、通信インフラのプロへ。",
  "全国の現場：案件特性に応じて移動や宿泊が伴う場合があります。配属・条件は選考時に確認します。",
  "チームで守る安全：個人の経験値に頼らず、手順と相互確認を重ねます。",
  "新しい3K：見た目も、働きがいも、人としての魅力も。古いイメージを更新する現場づくりを目指します。",
];

export default function RecruitPositionsSection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-[#E2E8F0] bg-white p-6 md:p-10"
      aria-labelledby="recruit-positions-heading"
    >
      <h2
        id="recruit-positions-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        募集ポジション（概要）
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        給与レンジは未確定のため「応相談／選考時にご説明」とします。詳細は随時更新します。
      </p>
      <ul className="mt-8 flex flex-col gap-6">
        {positions.map((job) => (
          <li
            key={job.title}
            className="rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-5"
          >
            <h3 className="text-lg font-bold text-[#0F172A]">{job.title}</h3>
            <ul className="mt-4 space-y-2">
              {job.bullets.map((b) => (
                <li key={b} className="flex gap-2 text-left text-sm text-[#475569]">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-[#2563eb]" aria-hidden />
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      <div className="mt-10 rounded-[12px] border border-[#BFDBFE] bg-[#EFF6FF] p-5">
        <h3 className="text-base font-bold text-[#0F172A]">働くイメージ（共有）</h3>
        <ul className="mt-3 list-inside list-disc space-y-2 text-left text-sm text-[#475569]">
          {valueProps.map((v) => (
            <li key={v}>{v}</li>
          ))}
        </ul>
      </div>
      <div className="mt-8 flex flex-wrap gap-3">
        <CtaButton href="/contact">採用について相談する</CtaButton>
      </div>
    </section>
  );
}
