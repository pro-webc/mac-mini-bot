export default function ContactPrivacySection() {
  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="privacy-detail-heading"
    >
      <h2 id="privacy-detail-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        個人情報の取り扱い（詳細）
      </h2>
      <div className="mt-4 space-y-3 text-left text-sm leading-relaxed text-[#475569]">
        <p>
          お問い合わせで取得した氏名・会社名・メールアドレス・電話番号・お問い合わせ内容は、ご返信および当社サービスのご案内に必要な範囲でのみ利用し、目的外利用や第三者への無断提供は行いません。
        </p>
        <p>
          送信により、お問い合わせ対応目的での連絡に同意したものとみなします。
        </p>
        <p>
          保管期間や開示・訂正・削除の手続きなど、さらに詳細なプライバシーポリシーは法務確認のうえで整備し、本ページまたは別ページからリンクを設置します。
        </p>
      </div>
    </section>
  );
}
