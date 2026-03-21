import TshFaqAccordionSection from "@/components/sections/TshFaqAccordionSection";
import TshFaqCtaSection from "@/components/sections/TshFaqCtaSection";
import TshFaqPageHeaderSection from "@/components/sections/TshFaqPageHeaderSection";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "よくある質問",
  description:
    "オンライン実施、人数目安、効果の捉え方、データ取扱い、料金、対応エリアなど、相談前によくあるご質問をまとめました。",
};

export default function FaqPage() {
  return (
    <>
      <TshFaqPageHeaderSection />
      <TshFaqAccordionSection />
      <TshFaqCtaSection />
    </>
  );
}
