import CtaButton from "@/components/CtaButton";
import { Banknote } from "lucide-react";

export default function TsServicePricingSection() {
  return (
    <section className="bg-[#F4F4F5] py-16 md:py-20" aria-labelledby="pricing-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="pricing-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          料金について
        </h2>
        <ul className="mt-8 space-y-4 border border-[#E4E4E7] bg-[#FFFFFF] p-4 md:p-6">
          <li className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            料金・時間・回数は案件により個別見積
          </li>
          <li className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            白ナンバー／緑ナンバー、人数、実施場所で変動
          </li>
          <li className="text-left text-sm leading-relaxed text-[#18181B] md:text-base">
            まずはヒアリングで最適な入り方を提案
          </li>
        </ul>
        <div className="mt-10">
          <CtaButton href="/contact">
            <Banknote className="h-5 w-5" aria-hidden />
            見積・条件を相談する
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
