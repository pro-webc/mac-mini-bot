/** 所在地の埋め込みURL。運用で NEXT_PUBLIC_GOOGLE_MAPS_EMBED_URL を設定してください。 */
export const OFFICE_MAP_EMBED_URL =
  process.env.NEXT_PUBLIC_GOOGLE_MAPS_EMBED_URL?.trim() ||
  "https://maps.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82&hl=ja&z=12&output=embed";
