import type { Metadata } from "next";
import ContactLineNoteSection from "@/components/sections/ContactLineNoteSection";
import RecruitFaqSection from "@/components/sections/RecruitFaqSection";
import RecruitFlowSection from "@/components/sections/RecruitFlowSection";
import RecruitHeroSection from "@/components/sections/RecruitHeroSection";
import RecruitPositionsSection from "@/components/sections/RecruitPositionsSection";
import RecruitTeaserSection from "@/components/sections/RecruitTeaserSection";

export const metadata: Metadata = {
  title: "採用情報",
  description:
    "未経験・経験者向けの一般的な訴求、勤務イメージのFAQ、応募・相談導線。確定条件は後差し替え。",
};

export default function RecruitPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 md:px-6">
      <RecruitHeroSection />
      <RecruitPositionsSection />
      <RecruitFlowSection />
      <RecruitFaqSection />
      <RecruitTeaserSection />
      <ContactLineNoteSection />
    </div>
  );
}
