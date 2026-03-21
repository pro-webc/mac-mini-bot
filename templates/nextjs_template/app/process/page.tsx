import TsHubStdProcessCtaSection from "@/components/sections/TsHubStdProcessCtaSection";
import TsHubStdProcessHeroSection from "@/components/sections/TsHubStdProcessHeroSection";
import TsHubStdProcessOnlineSection from "@/components/sections/TsHubStdProcessOnlineSection";
import TsHubStdProcessPrepSection from "@/components/sections/TsHubStdProcessPrepSection";
import TsHubStdProcessStepsSection from "@/components/sections/TsHubStdProcessStepsSection";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "導入の流れ",
  description:
    "お問い合わせから実施までのステップ、事前準備、オンライン対応について。日程と形式は相談しながら決められます。",
};

export default function ProcessPage() {
  return (
    <>
      <TsHubStdProcessHeroSection />
      <TsHubStdProcessStepsSection />
      <TsHubStdProcessPrepSection />
      <TsHubStdProcessOnlineSection />
      <TsHubStdProcessCtaSection />
    </>
  );
}
