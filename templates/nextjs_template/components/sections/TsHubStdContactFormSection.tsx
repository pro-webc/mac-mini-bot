"use client";

import Link from "next/link";
import { useState } from "react";
import { Send } from "lucide-react";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

const fleetOptions = ["1〜9台", "10〜19台", "20〜49台", "50台以上", "未定"] as const;

const contactMethods = ["メール", "電話（掲載後）", "オンライン面談"] as const;

export default function TsHubStdContactFormSection() {
  const [sent, setSent] = useState(false);

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    if (!form.reportValidity()) return;
    form.reset();
    setSent(true);
  }

  return (
    <section
      className="border border-[#E2E8F0] bg-[#FFFFFF] p-4 md:p-8"
      aria-labelledby="contact-form-heading"
    >
      <h2
        id="contact-form-heading"
        className="text-xl font-semibold text-[#0F172A] md:text-2xl"
      >
        お問い合わせフォーム
      </h2>
      <p className="mt-2 text-sm text-[#64748B]">
        3営業日以内を目安にご返信します。
      </p>

      {sent ? (
        <p
          className="mt-6 rounded-none border border-[#14B8A6] bg-[#F0FDFA] p-4 text-left text-sm text-[#0F172A]"
          role="status"
        >
          お問い合わせありがとうございます。内容を確認し、順次ご返信します。
        </p>
      ) : null}

      <form className="mt-8 space-y-6" onSubmit={onSubmit} noValidate>
        <div>
          <label
            htmlFor="company"
            className="block text-sm font-semibold text-[#0F172A]"
          >
            会社名
            <span className="text-[#0F766E]">（必須）</span>
          </label>
          <input
            id="company"
            name="company"
            type="text"
            required
            autoComplete="organization"
            placeholder="例：株式会社サンプル"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-semibold text-[#0F172A]">
            お名前
            <span className="text-[#0F766E]">（必須）</span>
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            autoComplete="name"
            placeholder="例：山田太郎"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-semibold text-[#0F172A]">
            メールアドレス
            <span className="text-[#0F766E]">（必須）</span>
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            inputMode="email"
            autoComplete="email"
            placeholder="例：xxxx@gmail.com"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <div>
          <label htmlFor="phone" className="block text-sm font-semibold text-[#0F172A]">
            電話番号
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="例：090-1234-5678"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <div>
          <label htmlFor="role" className="block text-sm font-semibold text-[#0F172A]">
            役職・担当
          </label>
          <input
            id="role"
            name="role"
            type="text"
            autoComplete="organization-title"
            placeholder="例：総務部 / 安全運転管理者"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <div>
          <label
            htmlFor="fleet_size_band"
            className="block text-sm font-semibold text-[#0F172A]"
          >
            社用車の保有台数（目安）
          </label>
          <select
            id="fleet_size_band"
            name="fleet_size_band"
            className="mt-2 w-full min-h-[48px] rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
            defaultValue=""
          >
            <option value="" disabled>
              選択してください
            </option>
            {fleetOptions.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="message" className="block text-sm font-semibold text-[#0F172A]">
            お問い合わせ内容
            <span className="text-[#0F766E]">（必須）</span>
          </label>
          <textarea
            id="message"
            name="message"
            required
            rows={6}
            autoComplete="off"
            placeholder="例：来月から四半期ごとに社内講習を実施したい。オンライン面談希望。対象はドライバー職20名程度。"
            className="mt-2 w-full min-h-[160px] min-w-[320px] max-w-full rounded-none border border-[#E2E8F0] bg-[#FFFFFF] px-3 py-2 text-base text-[#0F172A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
          />
        </div>

        <fieldset>
          <legend className="text-sm font-semibold text-[#0F172A]">
            希望する連絡方法
            <span className="text-[#0F766E]">（必須）</span>
          </legend>
          <div className="mt-3 flex flex-col gap-3">
            {contactMethods.map((m) => (
              <label
                key={m}
                className="inline-flex min-h-[44px] cursor-pointer items-center gap-3 text-base text-[#0F172A]"
              >
                <input
                  type="radio"
                  name="preferred_contact"
                  value={m}
                  required
                  className="h-4 w-4 accent-[#0F766E] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
                />
                {m}
              </label>
            ))}
          </div>
        </fieldset>

        <div className="rounded-none border border-[#E2E8F0] bg-[#FAFAF9] p-4">
          <label className="inline-flex min-h-[44px] cursor-pointer items-start gap-3 text-sm text-[#0F172A]">
            <input
              id="privacy_agree"
              name="privacy_agree"
              type="checkbox"
              required
              className="mt-1 h-4 w-4 accent-[#0F766E] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
            />
            <span>
              個人情報の取扱いに同意する
              <span className="text-[#0F766E]">（必須）</span>
              <br />
              <Link
                href="/contact#privacy"
                className="text-[#0F766E] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#14B8A6]"
              >
                個人情報の取扱いはこちら
              </Link>
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
