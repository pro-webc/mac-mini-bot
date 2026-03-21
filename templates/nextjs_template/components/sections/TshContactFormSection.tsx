"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function TshContactFormSection() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const form = e.currentTarget;
    const fd = new FormData(form);
    const name = String(fd.get("name") ?? "").trim();
    const company = String(fd.get("company") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const tel = String(fd.get("tel") ?? "").trim();
    const message = String(fd.get("message") ?? "").trim();

    if (!name || !company || !email || !tel || !message) {
      setError("未入力の項目があります。必須項目をご確認ください。");
      return;
    }
    if (!emailRe.test(email)) {
      setError("メールアドレスの形式をご確認ください。");
      return;
    }

    form.reset();
    setSent(true);
  }

  return (
    <section
      className="border border-[#e7e5e4] bg-[#ffffff] p-4 md:p-8"
      aria-labelledby="contact-form-heading"
    >
      <h2
        id="contact-form-heading"
        className="text-xl font-semibold text-[#1c1917] md:text-2xl"
      >
        お問い合わせフォーム
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-[#57534e]">
        送信後は内容確認の自動返信が無い場合もあります。担当より順次ご連絡します。
      </p>

      {sent ? (
        <p
          className="mt-6 border border-[#0f766e] bg-[#fafaf9] p-4 text-left text-sm text-[#1c1917]"
          role="status"
        >
          送信ありがとうございました。担当よりご連絡いたします。
        </p>
      ) : null}

      {error ? (
        <p className="mt-4 text-sm text-[#1c1917]" role="alert">
          {error}
        </p>
      ) : null}

      <form className="mt-8 space-y-6" onSubmit={onSubmit} noValidate>
        <div>
          <label
            htmlFor="tsh-name"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            お名前<span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="tsh-name"
            name="name"
            type="text"
            required
            autoComplete="name"
            placeholder="例：山田太郎"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-company"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            会社名<span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="tsh-company"
            name="company"
            type="text"
            required
            autoComplete="organization"
            placeholder="例：株式会社サンプル"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-dept"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            部署
          </label>
          <input
            id="tsh-dept"
            name="department"
            type="text"
            autoComplete="organization-title"
            placeholder="例：総務部"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-email"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            メールアドレス<span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="tsh-email"
            name="email"
            type="email"
            required
            inputMode="email"
            autoComplete="email"
            placeholder="例：xxxx@gmail.com"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-tel"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            電話番号<span className="text-[#0f766e]">（必須）</span>
          </label>
          <input
            id="tsh-tel"
            name="tel"
            type="tel"
            required
            inputMode="tel"
            autoComplete="tel"
            placeholder="例：099-000-0000"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-fleet"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            車両台数目安
          </label>
          <input
            id="tsh-fleet"
            name="fleet"
            type="text"
            placeholder="例：およそ25台（社用車中心）"
            className="mt-2 w-full min-h-[48px] min-w-0 rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <div>
          <label
            htmlFor="tsh-message"
            className="block text-sm font-semibold text-[#1c1917]"
          >
            相談内容<span className="text-[#0f766e]">（必須）</span>
          </label>
          <textarea
            id="tsh-message"
            name="message"
            required
            rows={5}
            placeholder="例：来期の管理者教育の位置づけを整理したい／走行評価の導入可否を知りたい"
            className="mt-2 w-full min-h-[160px] min-w-[320px] max-w-full rounded-none border border-[#e7e5e4] bg-[#ffffff] px-3 py-2 text-base text-[#1c1917] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0f766e]"
          />
        </div>
        <button
          type="submit"
          className={`${ctaButtonClass()} flex w-full min-h-[52px] items-center justify-center gap-2 text-base`}
        >
          <Send className="h-5 w-5 shrink-0" aria-hidden />
          内容を送信する
        </button>
      </form>
    </section>
  );
}
