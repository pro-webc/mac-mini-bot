export default function TrafficContactPageHeaderSection() {
  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-contact-h1"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h1
          id="traffic-contact-h1"
          className="text-left font-bold leading-[1.2] text-[#18181B]"
          style={{
            fontSize: "clamp(1.875rem, 1.5rem + 1vw, 2.5rem)",
          }}
        >
          お問い合わせ・相談予約
        </h1>
        <p className="mt-6 max-w-[65ch] text-left text-base leading-[1.75] text-[#52525B]">
          3営業日以内に返信（目安）。一人運営のため、繁忙期は返信が遅れる場合がある旨をあらかじめご了承ください。
        </p>
      </div>
    </section>
  );
}
