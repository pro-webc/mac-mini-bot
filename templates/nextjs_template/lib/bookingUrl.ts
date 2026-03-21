/** 外部予約（タイムレックス等）。ビルド時に NEXT_PUBLIC_BOOKING_URL で上書き可能。 */
export const BOOKING_URL =
  process.env.NEXT_PUBLIC_BOOKING_URL?.trim() || "https://example.com/booking";
