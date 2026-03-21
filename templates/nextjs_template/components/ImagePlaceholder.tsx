"use client";

type ImagePlaceholderProps = {
  description: string;
  aspectClassName?: string;
  className?: string;
  overlayText?: string;
};

/**
 * 実画像は置かず枠＋説明のみ（Unsplash 禁止・next/image の実ファイル参照禁止）。
 */
export default function ImagePlaceholder({
  description,
  aspectClassName = "aspect-video",
  className = "",
  overlayText,
}: ImagePlaceholderProps) {
  return (
    <div
      className={`relative flex w-full flex-col items-center justify-center overflow-hidden border-2 border-dashed border-[#334155] bg-[#1f2937] ${aspectClassName} ${className}`}
    >
      {overlayText ? (
        <p className="absolute inset-0 z-10 flex items-center justify-center bg-black/50 px-4 text-center text-base font-medium leading-snug text-[#eceff4]">
          {overlayText}
        </p>
      ) : null}
      <p className="max-w-prose px-4 text-center text-sm leading-[1.7] text-[#94a3b8]">
        {description}
      </p>
    </div>
  );
}
