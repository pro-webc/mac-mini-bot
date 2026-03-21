import type { Metadata } from "next";
import CompanyAccessMapSection from "@/components/sections/CompanyAccessMapSection";
import CompanyGroupContextSection from "@/components/sections/CompanyGroupContextSection";
import CompanyMessageSection from "@/components/sections/CompanyMessageSection";
import CompanyPageHeaderSection from "@/components/sections/CompanyPageHeaderSection";
import CompanyProfileTableSection from "@/components/sections/CompanyProfileTableSection";
import CompanyRecruitSection from "@/components/sections/CompanyRecruitSection";

export const metadata: Metadata = {
  title: "会社情報",
  description:
    "株式会社ワン・ピースの会社情報、代表メッセージ、会社概要、グループ文脈、アクセス（Google Maps）。",
};

export default function CompanyPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 md:px-6">
      <CompanyPageHeaderSection />
      <CompanyMessageSection />
      <CompanyProfileTableSection />
      <CompanyGroupContextSection />
      <CompanyAccessMapSection />
      <CompanyRecruitSection />
    </div>
  );
}
