import { Share2, ShieldAlert } from "lucide-react";

export default function TsHubStdServicesHabitSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="habit-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="habit-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          習慣の共有で、現場の言葉をそろえる
        </h2>
        <p className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          安全運転は個人スキルだけでなく、チームの前提共有が効いてきます。うまくいっている手順や確認ポイントを短い言葉に落とし、現場で再現できる形にします。
        </p>
        <ul className="mt-8 flex flex-col gap-4">
          <li className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-5">
            <Share2 className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              「うちの車両ではここが難しい」を共有し、具体策へ落とす
            </p>
          </li>
          <li className="flex gap-3 rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-5">
            <ShieldAlert className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              ヒヤリの共有が止まらない進行を目指す
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
