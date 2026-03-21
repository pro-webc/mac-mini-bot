"use client";

type GoogleMapEmbedProps = {
  embedUrl: string;
  title: string;
};

/** 所在地用 iframe のみ。画像・プレースホルダは置かない。 */
export default function GoogleMapEmbed({ embedUrl, title }: GoogleMapEmbedProps) {
  return (
    <div className="aspect-video w-full overflow-hidden bg-neutral-100">
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
