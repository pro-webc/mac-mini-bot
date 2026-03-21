import CtaButton from "@/components/CtaButton";

type Props = {
  h2: string;
  body: string[];
  secondaryCtaLabel: string;
};

export default function TsHubStdArticleFooterSection({
  h2,
  body,
  secondaryCtaLabel,
}: Props) {
  return (
    <section className="bg-[#FFFFFF] py-16 md:py-20" aria-labelledby="article-footer-h2">
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2
          id="article-footer-h2"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          {h2}
        </h2>
        {body.map((p, i) => (
          <p
            key={i}
            className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#0F172A]"
          >
            {p}
          </p>
        ))}
        <div className="mt-10">
          <CtaButton href="/contact" className="w-full justify-center sm:w-auto">
            {secondaryCtaLabel}
          </CtaButton>
        </div>
      </div>
    </section>
  );
}
