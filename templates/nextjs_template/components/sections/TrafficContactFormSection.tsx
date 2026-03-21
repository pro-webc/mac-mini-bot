"use client";

import { FormEvent, useState } from "react";
import { ArrowRight, Send } from "lucide-react";
import CtaButton from "@/components/CtaButton";

const contactOptions = [
  "メール",
  "電話（番号確定後）",
  "どちらでも可",
] as const;

function isValidEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

function isValidPhoneOptional(v: string) {
  if (!v.trim()) return true;
  const digits = v.replace(/\D/g, "");
  return digits.length >= 10 && digits.length <= 11;
}

const formIntro =
  "フォーム送信後、3営業日以内に返信します（目安）。一人運営のため、返信が遅れる場合はあらかじめご了承ください。内容によっては、日程調整用の外部リンク（例：タイムレックス）を返信でお送りします。";

const privacyNote =
  "取得した情報は、お問い合わせ対応とご提案のためにのみ使用し、目的外利用はしません。";

export default function TrafficContactFormSection() {
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const company = String(fd.get("company") ?? "").trim();
    const name = String(fd.get("name") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const phone = String(fd.get("phone") ?? "").trim();
    const vehicleContext = String(fd.get("vehicle_context") ?? "").trim();
    const needs = String(fd.get("needs") ?? "").trim();
    const preferredContact = String(fd.get("preferred_contact") ?? "").trim();
    const privacy = fd.get("privacy_agree");

    if (
      !company ||
      !name ||
      !email ||
      !vehicleContext ||
      !needs ||
      !preferredContact ||
      !privacy
    ) {
      setError(
        "入力内容を確認できませんでした。必須項目が埋まっているかご確認ください。",
      );
      return;
    }
    if (!isValidEmail(email)) {
      setError("メールアドレスの形式が正しいかご確認ください。");
      return;
    }
    if (!isValidPhoneOptional(phone)) {
      setError(
        "電話番号をご入力の場合は、数字の桁数（目安：10〜11桁）をご確認ください。",
      );
      return;
    }
    setError(null);
    setSent(true);
  };

  const inputClass =
    "mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488]";

  const textareaClass =
    "mt-2 min-h-[140px] w-full min-w-0 max-w-full resize-y border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488]";

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="traffic-contact-form-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="traffic-contact-form-heading"
          className="text-left font-semibold leading-[1.35] text-[#18181B]"
          style={{
            fontSize: "clamp(1.375rem, 1.2rem + 0.6vw, 1.75rem)",
            fontWeight: 650,
          }}
        >
          お問い合わせフォーム
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.75] text-[#18181B]">
          {formIntro}
        </p>
        <p className="mt-3 max-w-prose text-left text-sm leading-relaxed text-[#52525B]">
          {privacyNote}
        </p>

        {sent ? (
          <div
            className="mt-8 space-y-4 rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-6"
            role="status"
          >
            <p className="text-left text-base font-medium text-[#18181B]">
              お問い合わせありがとうございます。内容を受け付けました。
            </p>
            <p className="text-left text-sm leading-relaxed text-[#52525B]">
              {formIntro}
            </p>
            <p className="text-left text-xs text-[#52525B]">
              デモ実装のため、実際の送信処理は未接続です。本番ではサーバーアクションまたはフォームサービスへ接続してください。
            </p>
          </div>
        ) : (
          <form
            className="mt-8 max-w-prose space-y-6"
            onSubmit={onSubmit}
            noValidate
          >
            {error ? (
              <p
                className="rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-3 text-left text-sm text-[#18181B]"
                role="alert"
              >
                {error}
              </p>
            ) : null}

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
                className={inputClass}
              />
            </div>

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
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="role"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                役職・部署
              </label>
              <input
                id="role"
                name="role"
                type="text"
                autoComplete="organization-title"
                inputMode="text"
                placeholder="例：総務部 / 安全運転管理者"
                className={inputClass}
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
                placeholder="例：xxxx@company.co.jp"
                className={inputClass}
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
                placeholder="例：099-000-0000"
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="vehicle_context"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                社用車運用の概要
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <textarea
                id="vehicle_context"
                name="vehicle_context"
                autoComplete="off"
                inputMode="text"
                placeholder="例：白ナンバー中心／台数の目安／主な走行エリア"
                className={textareaClass}
              />
            </div>

            <div>
              <label
                htmlFor="needs"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                ご相談内容
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <textarea
                id="needs"
                name="needs"
                autoComplete="off"
                inputMode="text"
                placeholder="例：四半期に一度、管理者向けの短時間研修を検討／朝礼で使えるネタも欲しい"
                className={textareaClass}
              />
            </div>

            <div>
              <label
                htmlFor="preferred_contact"
                className="block text-left text-sm font-semibold text-[#18181B]"
              >
                希望の連絡方法
                <span className="text-[#0F766E]">（必須）</span>
              </label>
              <select
                id="preferred_contact"
                name="preferred_contact"
                autoComplete="off"
                className={`${inputClass} py-2`}
                defaultValue=""
              >
                <option value="" disabled>
                  選択してください
                </option>
                {contactOptions.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </div>

            <div className="rounded-sm border border-[#E4E4E7] bg-[#FAFAF9] p-4">
              <label className="flex cursor-pointer items-start gap-3 text-left text-sm text-[#18181B]">
                <input
                  type="checkbox"
                  name="privacy_agree"
                  value="1"
                  className="mt-1 h-5 w-5 shrink-0 border border-[#E4E4E7] text-[#0F766E] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0D9488]"
                />
                <span>
                  個人情報の取り扱いに同意する
                  <span className="text-[#0F766E]">（必須）</span>
                </span>
              </label>
            </div>

            <CtaButton type="submit" className="w-full justify-center md:max-w-none">
              <Send className="h-5 w-5 shrink-0" aria-hidden />
              <span>内容を確認して送信する</span>
              <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
            </CtaButton>
          </form>
        )}
      </div>
    </section>
  );
}
