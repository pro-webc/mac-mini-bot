"use client";

import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

type FieldErrors = Partial<
  Record<"name" | "email" | "phone" | "inquiry_type" | "message", string>
>;

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function countDigits(value: string) {
  return value.replace(/\D/g, "").length;
}

export default function ContactFormSection() {
  const [status, setStatus] = useState<"idle" | "sent" | "blocked">("idle");
  const [errors, setErrors] = useState<FieldErrors>({});

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const hp = (form.elements.namedItem("company_website") as HTMLInputElement)?.value;
    if (hp && hp.trim() !== "") {
      setStatus("blocked");
      return;
    }

    const name = (form.elements.namedItem("name") as HTMLInputElement).value.trim();
    const email = (form.elements.namedItem("email") as HTMLInputElement).value.trim();
    const phone = (form.elements.namedItem("phone") as HTMLInputElement).value.trim();
    const inquiryType = (form.elements.namedItem("inquiry_type") as HTMLSelectElement).value;
    const message = (form.elements.namedItem("message") as HTMLTextAreaElement).value.trim();

    const next: FieldErrors = {};
    if (!name) next.name = "お名前を入力してください。";
    if (!email) next.email = "メールアドレスを入力してください。";
    else if (!emailRe.test(email)) next.email = "メールアドレスの形式をご確認ください。";
    if (!phone) next.phone = "電話番号を入力してください。";
    else if (countDigits(phone) < 10)
      next.phone = "電話番号は数字で10桁以上入力してください。";
    if (!inquiryType) next.inquiry_type = "お問い合わせ種別を選択してください。";
    if (!message) next.message = "お問い合わせ内容を入力してください。";

    setErrors(next);
    if (Object.keys(next).length > 0) return;

    setStatus("sent");
    form.reset();
    setErrors({});
  }

  return (
    <section
      className="mt-12 overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="contact-form-heading"
    >
      <h2 id="contact-form-heading" className="text-xl font-bold text-[#0F172A] md:text-2xl">
        お問い合わせフォーム
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        3営業日以内を目安にご返信します。スパム対策のハニーポット欄を設けています（入力された場合は送信しません）。
      </p>

      {status === "sent" ? (
        <p
          className="mt-4 rounded-[12px] border border-[#86EFAC] bg-[#DCFCE7] p-4 text-sm font-medium text-[#166534]"
          role="status"
        >
          送信ありがとうございました。内容を確認のうえ、3営業日以内を目安にご返信します。
        </p>
      ) : null}
      {status === "blocked" ? (
        <p className="mt-4 text-sm text-[#475569]" role="status">
          送信を完了しました。
        </p>
      ) : null}

      <form className="mt-6 space-y-5" onSubmit={handleSubmit} noValidate>
        <input
          type="text"
          name="company_website"
          tabIndex={-1}
          autoComplete="off"
          aria-hidden
          className="absolute -left-[9999px] h-0 w-0 opacity-0"
        />
        <div>
          <label htmlFor="contact-name" className="block text-sm font-bold text-[#0F172A]">
            お名前 <span className="text-[#DC2626]">*</span>
          </label>
          <input
            id="contact-name"
            name="name"
            required
            placeholder="例：山田太郎"
            aria-invalid={errors.name ? true : undefined}
            aria-describedby={errors.name ? "contact-name-error" : undefined}
            className="mt-1 w-full min-w-0 max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          />
          {errors.name ? (
            <p id="contact-name-error" className="mt-1 text-sm text-[#DC2626]">
              {errors.name}
            </p>
          ) : null}
        </div>
        <div>
          <label htmlFor="contact-email" className="block text-sm font-bold text-[#0F172A]">
            メールアドレス <span className="text-[#DC2626]">*</span>
          </label>
          <input
            id="contact-email"
            name="email"
            type="email"
            required
            placeholder="例：xxxx@gmail.com"
            inputMode="email"
            autoComplete="email"
            aria-invalid={errors.email ? true : undefined}
            aria-describedby={errors.email ? "contact-email-error" : undefined}
            className="mt-1 w-full min-w-[320px] max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          />
          {errors.email ? (
            <p id="contact-email-error" className="mt-1 text-sm text-[#DC2626]">
              {errors.email}
            </p>
          ) : null}
        </div>
        <div>
          <label htmlFor="contact-phone" className="block text-sm font-bold text-[#0F172A]">
            電話番号 <span className="text-[#DC2626]">*</span>
          </label>
          <input
            id="contact-phone"
            name="phone"
            type="tel"
            required
            placeholder="例：090-1234-5678"
            inputMode="tel"
            autoComplete="tel"
            aria-invalid={errors.phone ? true : undefined}
            aria-describedby={errors.phone ? "contact-phone-error" : undefined}
            className="mt-1 w-full min-w-[320px] max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          />
          {errors.phone ? (
            <p id="contact-phone-error" className="mt-1 text-sm text-[#DC2626]">
              {errors.phone}
            </p>
          ) : null}
        </div>
        <div>
          <label htmlFor="contact-company" className="block text-sm font-bold text-[#0F172A]">
            会社名
          </label>
          <input
            id="contact-company"
            name="company"
            placeholder="例：株式会社サンプル"
            autoComplete="organization"
            className="mt-1 w-full min-w-[320px] max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          />
        </div>
        <div>
          <label htmlFor="contact-inquiry-type" className="block text-sm font-bold text-[#0F172A]">
            お問い合わせ種別 <span className="text-[#DC2626]">*</span>
          </label>
          <select
            id="contact-inquiry-type"
            name="inquiry_type"
            required
            defaultValue=""
            aria-invalid={errors.inquiry_type ? true : undefined}
            aria-describedby={errors.inquiry_type ? "contact-inquiry-type-error" : undefined}
            className="mt-1 w-full min-w-[320px] max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          >
            <option value="" disabled>
              選択してください
            </option>
            <option value="講習・研修の相談">講習・研修の相談</option>
            <option value="見積・提案依頼">見積・提案依頼</option>
            <option value="オンライン面談">オンライン面談</option>
            <option value="その他">その他</option>
          </select>
          {errors.inquiry_type ? (
            <p id="contact-inquiry-type-error" className="mt-1 text-sm text-[#DC2626]">
              {errors.inquiry_type}
            </p>
          ) : null}
        </div>
        <div>
          <label htmlFor="contact-message" className="block text-sm font-bold text-[#0F172A]">
            お問い合わせ内容 <span className="text-[#DC2626]">*</span>
          </label>
          <textarea
            id="contact-message"
            name="message"
            required
            rows={6}
            placeholder="例：来月から四半期ごとに社内講習を実施したい／運転評価の見える化を検討／オンライン面談希望"
            aria-invalid={errors.message ? true : undefined}
            aria-describedby={errors.message ? "contact-message-error" : undefined}
            className="mt-1 w-full min-w-[320px] max-w-full rounded-xl border border-[#CBD5E1] bg-[#FFFFFF] px-3 py-3 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
          />
          {errors.message ? (
            <p id="contact-message-error" className="mt-1 text-sm text-[#DC2626]">
              {errors.message}
            </p>
          ) : null}
        </div>
        <div className="rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <label className="flex cursor-pointer items-start gap-3 text-sm text-[#475569]">
            <input
              type="checkbox"
              name="consent"
              required
              className="mt-1 h-5 w-5 shrink-0 border-[#CBD5E1] text-[#2563eb] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
            />
            <span>
              <span className="font-bold text-[#0F172A]">個人情報の取り扱いに同意します</span>
              <span className="text-[#DC2626]"> *</span>
              <span className="mt-1 block text-xs leading-relaxed">
                送信により、お問い合わせ対応目的での連絡に同意したものとみなします。詳細はこのページの「個人情報の取り扱い（詳細）」をご確認ください。
              </span>
            </span>
          </label>
        </div>
        <button
          type="submit"
          className={`${ctaButtonClass()} inline-flex w-full min-h-[52px] items-center justify-center gap-2 text-base sm:w-full`}
        >
          <Send className="h-5 w-5 shrink-0" aria-hidden />
          送信する
        </button>
      </form>
    </section>
  );
}
