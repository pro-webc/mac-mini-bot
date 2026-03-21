import TsHubStdServicesCoachingSection from "@/components/sections/TsHubStdServicesCoachingSection";
import TsHubStdServicesCtaSection from "@/components/sections/TsHubStdServicesCtaSection";
import TsHubStdServicesEvalSection from "@/components/sections/TsHubStdServicesEvalSection";
import TsHubStdServicesFormatsSection from "@/components/sections/TsHubStdServicesFormatsSection";
import TsHubStdServicesHabitSection from "@/components/sections/TsHubStdServicesHabitSection";
import TsHubStdServicesHeroSection from "@/components/sections/TsHubStdServicesHeroSection";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "サービス",
  description:
    "法人向け交通安全教育・講習。コーチング型の対話、習慣の共有、GPSを用いた運転評価の見える化まで。",
};

export default function ServicesPage() {
  return (
    <>
      <TsHubStdServicesHeroSection />
      <TsHubStdServicesCoachingSection />
      <TsHubStdServicesHabitSection />
      <TsHubStdServicesEvalSection />
      <TsHubStdServicesFormatsSection />
      <TsHubStdServicesCtaSection />
    </>
  );
}
