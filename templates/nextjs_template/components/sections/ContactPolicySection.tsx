export default function ContactPolicySection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="contact-policy-heading"
    >
      <h2
        id="contact-policy-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        返信目安と個人情報の取り扱い（概要）
      </h2>
      <p className="mt-4 rounded-[12px] border border-[#caeb25]/50 bg-[#EFF6FF] p-4 text-left text-base font-semibold text-[#0F172A]">
        原則として、営業日以内にご返信いたします（目安日数は運用で設定）。
      </p>
      <p className="mt-6 text-left text-sm leading-relaxed text-[#475569]">
        取得した個人情報は、お問い合わせ対応目的での連絡に利用し、目的外利用はしません。詳細は下記の「個人情報の取り扱い（詳細）」をご確認ください。
      </p>
    </section>
  );
}
