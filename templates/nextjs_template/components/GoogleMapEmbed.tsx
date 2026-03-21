"use client";

type GoogleMapEmbedProps = {
  embedUrl: string;
  title: string;
  /** 親ラッパーに高さ制限などを付与する場合 */
  wrapperClassName?: string;
};

/** 所在地用 iframe のみ。画像・プレースホルダは置かない。 */
export default function GoogleMapEmbed({
  embedUrl,
  title,
  wrapperClassName = "",
}: GoogleMapEmbedProps) {
  return (
    <div
      className={`aspect-video w-full max-h-[min(52vw,280px)] overflow-hidden bg-neutral-100 md:max-h-none ${wrapperClassName}`.trim()}
    >
      <iframe
        title={title}
        src={embedUrl}
        className="h-full w-full border-0"
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
      />
    </div>
  );
}
