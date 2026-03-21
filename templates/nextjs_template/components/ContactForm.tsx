"use client";

import { useState } from "react";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

export default function ContactForm() {
  const [sent, setSent] = useState(false);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSent(true);
  };

  if (sent) {
    return (
      <div
        className="rounded-none border border-[#e7e5e4] bg-[#ffffff] p-6 md:p-8"
        role="status"
      >
        <h3 className="text-lg font-semibold text-[#0f172a]">
          送信ありがとうございます
        </h3>
        <p className="mt-3 max-w-prose text-base leading-[1.7] text-[#57534e]">
          内容を確認のうえ、メールまたはお電話でご連絡します。急ぎの場合は、フォームの電話番号欄に連絡可能な時間帯を併記ください。
        </p>
        <a
          href="/"
          className={`${ctaButtonClass()} mt-6 inline-flex w-full justify-center sm:w-auto`}
        >
          トップに戻る
        </a>
      </div>
    );
  }

  return (
    <form
      className="space-y-6 rounded-none border border-[#e7e5e4] bg-[#ffffff] p-6 md:p-8"
      onSubmit={onSubmit}
      noValidate
    >
      <p className="max-w-prose text-base leading-[1.7] text-[#57534e]">
        2営業日以内にご返信いたします（繁忙期は多少前後する場合があります）。
      </p>

      <div>
        <label
          htmlFor="company"
          className="block text-sm font-semibold text-[#0f172a]"
        >
          会社名
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <input
          id="company"
          name="company"
          type="text"
          required
          autoComplete="organization"
          placeholder="例：株式会社サンプル"
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] placeholder:text-[#a8a29e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label
          htmlFor="department"
          className="block text-sm font-semibold text-[#0f172a]"
        >
          部署・役職
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <input
          id="department"
          name="department"
          type="text"
          required
          autoComplete="organization-title"
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-semibold text-[#0f172a]">
          氏名
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          autoComplete="name"
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label htmlFor="tel" className="block text-sm font-semibold text-[#0f172a]">
          電話番号
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <input
          id="tel"
          name="tel"
          type="tel"
          required
          inputMode="tel"
          autoComplete="tel"
          placeholder="例：099-000-0000"
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] placeholder:text-[#a8a29e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-semibold text-[#0f172a]">
          メールアドレス
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          inputMode="email"
          autoComplete="email"
          placeholder="例：name@example.com"
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] placeholder:text-[#a8a29e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label htmlFor="fleet" className="block text-sm font-semibold text-[#0f172a]">
          車両台数の目安
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <p className="mt-1 text-sm text-[#57534e]">
          台数が未定の場合は「未定（概算で可）」とご記入ください。
        </p>
        <input
          id="fleet"
          name="fleet"
          type="text"
          required
          className="mt-2 w-full min-h-[48px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <div>
        <label
          htmlFor="message"
          className="block text-sm font-semibold text-[#0f172a]"
        >
          相談内容
          <span className="ml-1 text-[#0f766e]">（必須）</span>
        </label>
        <textarea
          id="message"
          name="message"
          required
          rows={6}
          placeholder="3月中に管理者向けの講習を検討／オンライン可否を知りたい／評価の説明方法を社内に展開したい など"
          className="mt-2 w-full min-h-[160px] max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-4 py-3 text-base text-[#0f172a] placeholder:text-[#a8a29e] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
        />
      </div>

      <button type="submit" className={`${ctaButtonClass()} w-full min-h-[52px] text-[17px]`}>
        内容を送信する
      </button>

      <p
        id="privacy_compact"
        className="max-w-prose text-sm leading-relaxed text-[#57534e]"
      >
        お預かりした個人情報は、ご返信と講習準備の目的に限り利用します。
      </p>
    </form>
  );
}
