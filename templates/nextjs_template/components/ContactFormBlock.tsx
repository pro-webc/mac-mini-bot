"use client";

import { FormEvent, useState } from "react";

import { ctaButtonClass } from "@/lib/ctaButtonClass";

export default function ContactFormBlock() {
  const [submitted, setSubmitted] = useState(false);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <p
        className="border border-[#e7e5e4] bg-[#fafaf9] p-6 text-left text-base leading-[1.7] text-[#0f172a]"
        role="status"
      >
        お問い合わせありがとうございます。内容を確認のうえ、ご登録のメールアドレスへ返信いたします。
      </p>
    );
  }

  return (
    <form
      className="border border-[#e7e5e4] bg-[#ffffff] p-6 md:p-8"
      onSubmit={onSubmit}
      noValidate
    >
      <div className="space-y-6">
        <div>
          <label
            htmlFor="company"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            企業名
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="company"
            name="company"
            type="text"
            required
            autoComplete="organization"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：株式会社サンプル"
          />
        </div>

        <div>
          <label
            htmlFor="dept"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            部署・役職
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="dept"
            name="dept"
            type="text"
            required
            autoComplete="organization-title"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：総務部 課長"
          />
        </div>

        <div>
          <label
            htmlFor="name"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            お名前
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            autoComplete="name"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：山田太郎"
          />
        </div>

        <div>
          <label
            htmlFor="email"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            メールアドレス
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            inputMode="email"
            autoComplete="email"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：xxxx@gmail.com"
          />
        </div>

        <div>
          <label
            htmlFor="tel"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            電話番号
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="tel"
            name="tel"
            type="tel"
            required
            inputMode="tel"
            autoComplete="tel"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：090-1234-5678"
          />
        </div>

        <div>
          <label
            htmlFor="body"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            相談内容
            <span className="text-[#0f766e]">（必須）</span>
          </label>
          <textarea
            id="body"
            name="body"
            required
            rows={6}
            className="mt-2 w-full min-h-[160px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：4月から年2回の集合研修を検討している／複数拠点でオンライン併用したい／朝礼で使える短いネタを増やしたい"
          />
        </div>

        <div>
          <label
            htmlFor="timepref"
            className="block text-sm font-semibold text-[#0f172a]"
          >
            希望連絡時間帯（任意）
          </label>
          <input
            id="timepref"
            name="timepref"
            type="text"
            autoComplete="off"
            className="mt-2 w-full min-h-[48px] min-w-0 max-w-full rounded-none border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2 text-base text-[#0f172a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
            placeholder="例：平日10時〜17時"
          />
        </div>
      </div>

      <p className="mt-6 text-left text-sm leading-[1.7] text-[#57534e]">
        取得した情報は、ご相談への返信および講習設計のために利用し、目的外利用や無断での第三者提供は行いません。
      </p>

      <button
        type="submit"
        className={`${ctaButtonClass()} mt-8 w-full min-h-[52px] text-base sm:text-lg`}
      >
        内容を送信する
      </button>
    </form>
  );
}
