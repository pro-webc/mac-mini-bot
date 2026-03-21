import type { Metadata } from "next";
import KgsMeasCtaSection from "@/components/sections/KgsMeasCtaSection";
import KgsMeasCycleDiagramSection from "@/components/sections/KgsMeasCycleDiagramSection";
import KgsMeasDeliverablesSection from "@/components/sections/KgsMeasDeliverablesSection";
import KgsMeasPageHeaderSection from "@/components/sections/KgsMeasPageHeaderSection";
import KgsMeasPrivacySection from "@/components/sections/KgsMeasPrivacySection";
import KgsMeasWhatWeMeasureSection from "@/components/sections/KgsMeasWhatWeMeasureSection";

export const metadata: Metadata = {
  title: "見える化・評価",
  description:
    "一般道コース走行を想定した技能・癖の傾向の見える化。測定の考え方、PDCAの置き方、データと個人情報の扱い。",
};

export default function MeasurementPage() {
  return (
    <>
      <KgsMeasPageHeaderSection />
      <KgsMeasWhatWeMeasureSection />
      <KgsMeasCycleDiagramSection />
      <KgsMeasPrivacySection />
      <KgsMeasDeliverablesSection />
      <KgsMeasCtaSection />
    </>
  );
}
