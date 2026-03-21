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
      className={`relative flex w-full flex-col items-center justify-center overflow-hidden border-2 border-dashed border-neutral-300 bg-neutral-50 ${aspectClassName} ${className}`}
    >
      {overlayText ? (
        <p className="absolute inset-0 z-10 flex items-center justify-center bg-black/40 px-4 text-center text-base font-medium text-white">
          {overlayText}
        </p>
      ) : null}
      <p className="max-w-prose px-4 text-center text-sm leading-relaxed text-neutral-700">
        {description}
      </p>
    </div>
  );
}
