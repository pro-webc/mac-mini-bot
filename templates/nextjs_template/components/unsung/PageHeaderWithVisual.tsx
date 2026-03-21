import ImagePlaceholder from "@/components/ImagePlaceholder";

type PageHeaderWithVisualProps = {
  title: string;
  lead: string;
  visualDescription: string;
  visualOverlay?: string;
  aspectClassName?: string;
};

export default function PageHeaderWithVisual({
  title,
  lead,
  visualDescription,
  visualOverlay,
  aspectClassName = "aspect-[4/3] md:aspect-[21/9]",
}: PageHeaderWithVisualProps) {
  return (
    <header className="border-b border-[#334155]">
      <div className="mx-auto max-w-6xl px-4 py-14 md:px-6 md:py-20">
        <h1 className="max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-[#eceff4] sm:text-4xl md:text-[2.75rem] md:leading-tight">
          {title}
        </h1>
        <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
          {lead}
        </p>
        <div className="mt-10">
          <ImagePlaceholder
            description={visualDescription}
            aspectClassName={aspectClassName}
            overlayText={visualOverlay}
          />
        </div>
      </div>
    </header>
  );
}
