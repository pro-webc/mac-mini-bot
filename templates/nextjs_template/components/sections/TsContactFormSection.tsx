"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

const contactMethodOptions = ["メール", "電話", "どちらでも可"] as const;

function isValidEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

function isValidPhoneOptional(v: string) {
  if (!v.trim()) return true;
  const digits = v.replace(/\D/g, "");
  return digits.length >= 10 && digits.length <= 11;
}

export default function TsContactFormSection() {
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const name = String(fd.get("name") ?? "").trim();
    const company = String(fd.get("company") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const phone = String(fd.get("phone") ?? "").trim();
    const message = String(fd.get("message") ?? "").trim();
    const contactMethod = String(fd.get("contactMethod") ?? "");
    const privacy = fd.get("privacy");

    if (!name || !company || !email || !message || !contactMethod || !privacy) {
      setError("未入力の項目があります。各項目をご確認ください。");
      return;
    }
    if (!isValidEmail(email)) {
      setError("メールアドレスの形式をご確認ください。");
      return;
    }
    if (!isValidPhoneOptional(phone)) {
      setError(
        "電話番号はハイフンあり／なしどちらでも構いません。数字をご確認ください。",
      );
      return;
    }
    setError(null);
    setSent(true);
  };

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      aria-labelledby="contact-form-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="contact-form-heading"
          className="text-left text-xl font-semibold text-[#18181B] md:text-2xl"
        >
          お問い合わせフォーム
        </h2>
        <p className="mt-4 max-w-prose text-left text-sm leading-relaxed text-[#18181B] md:text-base">
          3営業日以内にご返信します（目安）。お急ぎの場合は電話（番号は準備中）もご利用ください。送信内容は相談の事前整理に使い、秘密保持に配慮して取り扱います。
        </p>
        <p className="mt-2 text-left text-sm text-[#52525B]">
          プライバシー方針は確定次第リンク
        </p>

        {sent ? (
          <p
            className="mt-8 rounded-none border border-[#E4E4E7] bg-[#FAFAF9] p-4 text-left text-sm text-[#18181B]"
            role="status"
          >
            デモ表示です。本番では送信処理をサーバー側に接続してください。
          </p>
        ) : (
          <form
            className="mt-8 max-w-prose space-y-6"
            onSubmit={onSubmit}
            noValidate
          >
            {error ? (
              <p
                className="rounded-none border border-[#E4E4E7] bg-[#FAFAF9] p-3 text-left text-sm text-[#18181B]"
                role="alert"
              >
                {error}
              </p>
            ) : null}

            <div>
              <label
                htmlFor="name"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                お名前
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                inputMode="text"
                placeholder="例：山田太郎"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="company"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                会社名
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <input
                id="company"
                name="company"
                type="text"
                autoComplete="organization"
                inputMode="text"
                placeholder="例：株式会社サンプル"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="department"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                部署・役職
              </label>
              <input
                id="department"
                name="department"
                type="text"
                autoComplete="organization-title"
                inputMode="text"
                placeholder="例：総務部 課長"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                メールアドレス
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                placeholder="例：xxxx@gmail.com"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="phone"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                電話番号
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                autoComplete="tel"
                inputMode="tel"
                placeholder="例：090-1234-5678"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="vehicleCount"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                車両台数目安
              </label>
              <input
                id="vehicleCount"
                name="vehicleCount"
                type="text"
                autoComplete="off"
                inputMode="numeric"
                placeholder="例：25台（不明なら未記入で可）"
                className="mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="message"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                相談内容
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <textarea
                id="message"
                name="message"
                rows={5}
                autoComplete="off"
                inputMode="text"
                placeholder="例：来月から新入社員向けに出庫前教育を月1回したい／安全運転管理者向け講習の実施形態を相談したい"
                className="mt-2 w-full min-w-[320px] max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
            </div>

            <div>
              <label
                htmlFor="contactMethod"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                希望連絡手段
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <select
                id="contactMethod"
                name="contactMethod"
                autoComplete="off"
                defaultValue=""
                className="mt-2 min-h-[48px] w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              >
                <option value="" disabled>
                  選択してください
                </option>
                {contactMethodOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-start gap-3 border border-[#E4E4E7] bg-[#FAFAF9] p-4">
              <input
                id="privacy"
                name="privacy"
                type="checkbox"
                value="1"
                className="mt-1 h-5 w-5 shrink-0 border-[#E4E4E7] text-[#0F766E] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
              />
              <label htmlFor="privacy" className="text-left text-sm text-[#18181B]">
                個人情報の取り扱いに同意
                <span className="text-[#0F766E]">（必須）</span>
              </label>
            </div>

            <button
              type="submit"
              className="flex w-full min-h-[52px] items-center justify-center gap-2 rounded-[12px] bg-[#0F766E] px-6 py-3 text-base font-semibold text-[#FFFFFF] hover:bg-[#115E59] active:bg-[#0d5c56] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E] motion-safe:transition-colors md:max-w-md"
            >
              <Send className="h-5 w-5" aria-hidden />
              内容を送信する
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
