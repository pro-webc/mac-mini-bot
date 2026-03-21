import type { Metadata } from "next";
import TsHubApproachHeaderSection from "@/components/sections/TsHubApproachHeaderSection";
import TsHubApproachPhilosophySection from "@/components/sections/TsHubApproachPhilosophySection";
import TsHubApproachFacilitationSection from "@/components/sections/TsHubApproachFacilitationSection";
import TsHubApproachMeasurementPrivacySection from "@/components/sections/TsHubApproachMeasurementPrivacySection";
import TsHubApproachDeliverablesSection from "@/components/sections/TsHubApproachDeliverablesSection";
import TsHubApproachCtaSection from "@/components/sections/TsHubApproachCtaSection";

export const metadata: Metadata = {
  title: "進め方・考え方",
};

export default function ApproachPage() {
  return (
    <>
      <TsHubApproachHeaderSection />
      <TsHubApproachPhilosophySection />
      <TsHubApproachFacilitationSection />
      <TsHubApproachMeasurementPrivacySection />
      <TsHubApproachDeliverablesSection />
      <TsHubApproachCtaSection />
    </>
  );
}
