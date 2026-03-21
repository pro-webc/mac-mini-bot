"use client";

import { useState, type FormEvent } from "react";

import { ctaButtonClass } from "@/lib/ctaButtonClass";

export default function ContactFormSection() {
  const [submitted, setSubmitted] = useState(false);

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <section
      className="py-16 md:py-24"
      aria-labelledby="contact-form-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="contact-form-heading"
          className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
        >
          お問い合わせフォーム
        </h2>
        <p className="mt-4 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
          3営業日以内を目安にご返信いたします（繁忙期は前後する場合があります）。
        </p>
        <p className="mt-3 max-w-prose text-sm leading-[1.7] text-[#94a3b8]">
          個人情報の取り扱いは
          <a
            href="#privacy"
            className="text-[#eceff4] underline-offset-4 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
          >
            プライバシーポリシー
          </a>
          をご確認ください。
        </p>

        {submitted ? (
          <p
            className="mt-8 rounded-[14px] border border-[#334155] bg-[#1f2937] p-6 text-base leading-[1.7] text-[#eceff4]"
            role="status"
          >
            お問い合わせありがとうございます。内容を確認のうえ、ご登録のメール宛に返信いたします。
          </p>
        ) : (
          <form
            className="mt-8 max-w-prose space-y-6"
            onSubmit={onSubmit}
            noValidate
          >
            <div>
              <label
                htmlFor="company"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                会社名
                <span className="text-[#94a3b8]">（必須）</span>
              </label>
              <input
                id="company"
                name="company"
                type="text"
                required
                autoComplete="organization"
                placeholder="例：株式会社サンプル"
                className="mt-2 min-h-[48px] w-full min-w-0 rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base text-[#eceff4] placeholder:text-[#64748b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              />
            </div>
            <div>
              <label
                htmlFor="fullname"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                お名前
                <span className="text-[#94a3b8]">（必須）</span>
              </label>
              <input
                id="fullname"
                name="fullname"
                type="text"
                required
                autoComplete="name"
                placeholder="例：山田太郎"
                className="mt-2 min-h-[48px] w-full min-w-0 rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base text-[#eceff4] placeholder:text-[#64748b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              />
            </div>
            <div>
              <label
                htmlFor="jobtitle"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                役職
              </label>
              <input
                id="jobtitle"
                name="jobtitle"
                type="text"
                autoComplete="organization-title"
                className="mt-2 min-h-[48px] w-full min-w-0 rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base text-[#eceff4] placeholder:text-[#64748b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              />
            </div>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                メールアドレス
                <span className="text-[#94a3b8]">（必須）</span>
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                inputMode="email"
                placeholder="例：name@company.com"
                className="mt-2 min-h-[48px] w-full min-w-0 rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base text-[#eceff4] placeholder:text-[#64748b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              />
            </div>
            <div>
              <label
                htmlFor="headcount"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                従業員規模の目安
              </label>
              <select
                id="headcount"
                name="headcount"
                className="mt-2 min-h-[48px] w-full min-w-0 rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base text-[#eceff4] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
                defaultValue=""
              >
                <option value="" disabled>
                  選択してください
                </option>
                <option value="to300">〜300名</option>
                <option value="301to1000">301〜1,000名</option>
                <option value="1001plus">1,001名〜</option>
              </select>
            </div>
            <div>
              <label
                htmlFor="message"
                className="block text-sm font-semibold text-[#eceff4]"
              >
                ご相談内容
                <span className="text-[#94a3b8]">（必須）</span>
              </label>
              <textarea
                id="message"
                name="message"
                required
                rows={6}
                placeholder="例：次世代幹部向けプログラムの実施時期と人数について相談したい／1,000名規模組織での展開可否を知りたい"
                className="mt-2 w-full min-w-[min(100%,320px)] max-w-full rounded-[12px] border border-[#334155] bg-[#111827] px-4 py-3 text-base leading-[1.7] text-[#eceff4] placeholder:text-[#64748b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
              />
            </div>
            <div className="rounded-[12px] border border-[#334155] bg-[#111827] p-4">
              <div className="flex gap-3">
                <input
                  id="privacy-agree"
                  name="privacy-agree"
                  type="checkbox"
                  required
                  className="mt-1 h-5 w-5 shrink-0 rounded border-[#334155] bg-[#1f2937] text-[#eceff4] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4]"
                />
                <label
                  htmlFor="privacy-agree"
                  className="text-sm leading-[1.7] text-[#eceff4]"
                >
                  個人情報の取り扱いに同意する
                  <span className="text-[#94a3b8]">（必須）</span>
                </label>
              </div>
            </div>
            <button
              type="submit"
              className={`${ctaButtonClass()} w-full justify-center sm:max-w-none`}
            >
              内容を送信する
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
