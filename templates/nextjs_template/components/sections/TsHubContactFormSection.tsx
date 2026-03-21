"use client";

import { useFormState } from "react-dom";
import { ArrowRight } from "lucide-react";
import {
  submitContactForm,
  type ContactFormState,
} from "@/lib/contactFormActions";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

const topicOptions = [
  "研修・教育の相談",
  "見える化（評価）の相談",
  "朝礼Tips・継続支援の相談",
  "その他",
];

const initial: ContactFormState = { ok: false, message: "" };

export default function TsHubContactFormSection() {
  const [state, formAction] = useFormState(submitContactForm, initial);

  if (state.ok) {
    return (
      <section
        id="contact-form"
        className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
      >
        <div className="mx-auto max-w-2xl px-4 md:px-6">
          <div
            className="border border-[#E4E4E7] bg-[#FAFAF9] p-6 text-left"
            role="status"
          >
            <p className="text-base font-medium text-[#18181B]">
              {state.message}
            </p>
          </div>
        </div>
      </section>
    );
  }

  const err = state.fieldErrors ?? {};

  return (
    <section
      id="contact-form"
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-20"
    >
      <div className="mx-auto max-w-2xl px-4 md:px-6">
        <h2 className="text-left text-xl font-bold text-[#18181B] md:text-2xl">
          お問い合わせフォーム
        </h2>
        <p className="mt-4 text-left text-sm leading-relaxed text-[#52525B] md:text-base">
          2営業日以内に返信いたします（繁忙期は前後する場合があります）。
        </p>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-left text-sm text-[#52525B]">
          <li>まずは分かる範囲でご入力ください。未確定の項目は「未定」で構いません。</li>
          <li>相談内容は箇条書きで十分です。</li>
          <li>社外秘として扱い、目的外利用はしません。</li>
        </ul>

        {!state.ok && state.message ? (
          <p
            className="mt-4 border-l-4 border-[#1D4ED8] pl-3 text-left text-sm text-[#18181B]"
            role="alert"
          >
            {state.message}
          </p>
        ) : null}

        <form action={formAction} className="mt-8 space-y-5" noValidate>
          <div>
            <label
              htmlFor="company"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              会社名
              <span className="font-semibold text-[#1D4ED8]">（必須）</span>
            </label>
            <input
              id="company"
              name="company"
              type="text"
              autoComplete="organization"
              inputMode="text"
              placeholder="例：株式会社サンプル"
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
            {err.company ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.company}</p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor="department"
              className="block text-left text-sm font-medium text-[#18181B]"
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
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
          </div>

          <div>
            <label
              htmlFor="name"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              お名前
              <span className="font-semibold text-[#1D4ED8]">（必須）</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              autoComplete="name"
              inputMode="text"
              placeholder="例：山田太郎"
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
            {err.name ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.name}</p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              メールアドレス
              <span className="font-semibold text-[#1D4ED8]">（必須）</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="例：yamada@example.com"
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
            {err.email ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.email}</p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor="phone"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              電話番号
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              placeholder="例：099-1234-5678"
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
            {err.phone ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.phone}</p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor="topic"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              ご相談の種類
              <span className="font-semibold text-[#1D4ED8]">（必須）</span>
            </label>
            <select
              id="topic"
              name="topic"
              defaultValue=""
              className="mt-1 w-full min-h-[48px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            >
              <option value="" disabled>
                選択してください
              </option>
              {topicOptions.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
            {err.topic ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.topic}</p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor="message"
              className="block text-left text-sm font-medium text-[#18181B]"
            >
              ご相談内容
              <span className="font-semibold text-[#1D4ED8]">（必須）</span>
            </label>
            <textarea
              id="message"
              name="message"
              rows={6}
              inputMode="text"
              placeholder="例：3月に新入社員向けの交通安全教育を検討している。集合とオンラインの併用可否を知りたい。"
              className="mt-1 w-full min-h-[160px] border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-2 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
            />
            {err.message ? (
              <p className="mt-1 text-left text-sm text-[#52525B]">{err.message}</p>
            ) : null}
          </div>

          <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-4">
            <label className="flex cursor-pointer items-start gap-3 text-left">
              <input
                type="checkbox"
                name="consent"
                className="mt-1 h-5 w-5 shrink-0 border border-[#E4E4E7] text-[#1D4ED8] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
              />
              <span className="text-sm text-[#18181B]">
                個人情報の取り扱いに同意する
                <span className="font-semibold text-[#1D4ED8]">（必須）</span>
              </span>
            </label>
            {err.consent ? (
              <p className="mt-2 text-left text-sm text-[#52525B]">{err.consent}</p>
            ) : null}
          </div>

          <button
            type="submit"
            className={`${ctaButtonClass()} w-full min-h-[52px] text-base sm:w-full`}
          >
            <span>無料で相談する</span>
            <ArrowRight className="h-5 w-5 shrink-0" aria-hidden />
          </button>
        </form>
      </div>
    </section>
  );
}
