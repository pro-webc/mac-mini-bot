import type { Metadata } from "next";
import TsHubPrivacyHeaderSection from "@/components/sections/TsHubPrivacyHeaderSection";
import TsHubPrivacyBodySection from "@/components/sections/TsHubPrivacyBodySection";
import TsHubPrivacyDrivingSection from "@/components/sections/TsHubPrivacyDrivingSection";
import TsHubPrivacyContactFooterSection from "@/components/sections/TsHubPrivacyContactFooterSection";

export const metadata: Metadata = {
  title: "個人情報の取扱い",
};

export default function PrivacyPage() {
  return (
    <>
      <TsHubPrivacyHeaderSection />
      <TsHubPrivacyBodySection />
      <TsHubPrivacyDrivingSection />
      <TsHubPrivacyContactFooterSection />
    </>
  );
}
