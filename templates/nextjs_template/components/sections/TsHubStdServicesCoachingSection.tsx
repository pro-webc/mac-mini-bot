import { Sparkles, GitMerge } from "lucide-react";

export default function TsHubStdServicesCoachingSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="coaching-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="coaching-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          コーチング型で進める理由
        </h2>
        <p className="mt-8 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
          一方通行の講義は、知識は増えても現場の行動が変わりにくいことがあります。TS-hubでは、質問と振り返りを軸に、参加者自身の言葉で「やる理由」と「やり方」を作っていきます。
        </p>
        <ul className="mt-8 flex flex-col gap-4 md:flex-row md:gap-6">
          <li className="flex flex-1 gap-3 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-5">
            <Sparkles className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              正しさの押し付けにならない進行を重視する
            </p>
          </li>
          <li className="flex flex-1 gap-3 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] p-5">
            <GitMerge className="mt-0.5 h-6 w-6 shrink-0 text-[#0F766E]" aria-hidden />
            <p className="text-left text-base leading-[1.7] text-[#0F172A]">
              部署や年齢層が混在しても、対話の型で収束しやすい
            </p>
          </li>
        </ul>
      </div>
    </section>
  );
}
