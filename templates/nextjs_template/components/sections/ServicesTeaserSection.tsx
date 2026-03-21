import Link from "next/link";
import { Headphones, Droplets, Home, Wrench } from "lucide-react";

const items = [
  {
    icon: Home,
    title: "自宅に寄り添う訪問対応",
    body: "ご自宅での施工を前提に、事前のご説明と段取りを大切にしています。",
  },
  {
    icon: Droplets,
    title: "水まわりのイメージ整理",
    body: "清潔感のある仕上がりを目指しつつ、現場状況に合わせてご提案します（詳細業種は確定待ち）。",
  },
  {
    icon: Wrench,
    title: "現場での丁寧な確認",
    body: "道具の音や作業範囲など、不安になりやすい点はできるだけ言葉にして共有します。",
  },
  {
    icon: Headphones,
    title: "アフターフォロー志向",
    body: "長く付き合える関係を意識し、完了後のご相談窓口も設けていく方針です。",
  },
];

export default function ServicesTeaserSection() {
  return (
    <section className="bg-[#F8FAFC] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] md:text-3xl">
          サービス概要
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#475569]">
          設備・内装・外構などの正式なラベルや対応範囲は、確定情報に基づきサービスページで補足していきます。
        </p>
        <ul className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {items.map((item) => (
            <li
              key={item.title}
              className="flex flex-col rounded-[20px] border border-[#E2E8F0] bg-[#FFFFFF] p-6"
            >
              <item.icon className="h-8 w-8 text-[#0EA5E9]" aria-hidden />
              <h3 className="mt-4 text-lg font-semibold text-[#0F172A]">
                {item.title}
              </h3>
              <p className="mt-2 flex-1 text-left text-sm leading-relaxed text-[#475569]">
                {item.body}
              </p>
            </li>
          ))}
        </ul>
        <div className="mt-10 text-center">
          <Link
            href="/services"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center rounded-[14px] bg-[#0284C7] px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-[#0369A1] active:bg-[#075985] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0284C7]"
          >
            サービスの詳細を見る
          </Link>
        </div>
      </div>
    </section>
  );
}
