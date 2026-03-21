"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";
import { ctaButtonClass } from "@/lib/ctaButtonClass";

function isValidEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

const formIntro =
  "下記フォームからお送りいただいた内容をもとに、実施形態のたたき台と次の打合せ案内を返信します。個人情報はお問い合わせ対応の目的に限り利用します。";

const privacyNote =
  "送信前に個人情報の取り扱い（要ページ：プライバシーポリシーは確定後に整備）へ同意いただくチェックを置くことを推奨。";

const successMessage =
  "お問い合わせを受け付けました。3営業日以内にご返信します。急ぎの場合は予約ツールから日程調整もご利用ください。";

export default function KgsContactFormSection() {
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const company = String(fd.get("company") ?? "").trim();
    const name = String(fd.get("name") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const phone = String(fd.get("phone") ?? "").trim();
    const message = String(fd.get("message") ?? "").trim();
    const privacy = fd.get("privacy_agree");

    if (!company || !name || !email || !message || !privacy) {
      setError(
        "入力内容を確認できませんでした。必須項目が埋まっているかご確認ください。",
      );
      return;
    }
    if (!isValidEmail(email)) {
      setError("メールアドレスの形式が正しいかご確認ください。");
      return;
    }
    if (phone) {
      const digits = phone.replace(/\D/g, "");
      if (digits.length < 10 || digits.length > 11) {
        setError(
          "電話番号をご入力の場合は、数字の桁数（目安：10〜11桁）をご確認ください。",
        );
        return;
      }
    }
    setError(null);
    setSent(true);
  };

  const inputClass =
    "mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]";

  const textareaClass =
    "mt-2 min-h-[140px] w-full min-w-0 max-w-full resize-y border border-[#E4E4E7] bg-[#FFFFFF] px-3 py-3 text-base text-[#18181B] placeholder:text-[#52525B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]";

  const selectClass =
    "mt-2 min-h-[48px] w-full min-w-0 max-w-full border border-[#E4E4E7] bg-[#FFFFFF] px-3 text-base text-[#18181B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]";

  return (
    <section
      className="border-b border-[#E4E4E7] bg-[#FFFFFF] py-16 md:py-24"
      aria-labelledby="kgs-contact-form-h2"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="kgs-contact-form-h2"
          className="text-left text-2xl font-bold tracking-tight text-[#18181B] md:text-3xl"
        >
          お問い合わせフォーム
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-relaxed text-[#18181B]">
          {formIntro}
        </p>
        <p className="mt-3 max-w-prose text-left text-sm leading-relaxed text-[#52525B]">
          {privacyNote}
        </p>

        {sent ? (
          <div
            className="mt-8 space-y-4 border border-[#E4E4E7] bg-[#FAFAF9] p-6"
            role="status"
          >
            <p className="text-left text-base font-medium text-[#18181B]">
              {successMessage}
            </p>
            <p className="text-left text-xs text-[#52525B]">
              デモ実装のため送信処理は未接続です。本番ではメール送信サービス等へ接続してください。
            </p>
          </div>
        ) : (
          <form
            className="mt-8 max-w-prose space-y-6"
            onSubmit={onSubmit}
            noValidate
          >
            <div>
              <label
                htmlFor="company"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                会社名
                <span className="text-[#1D4ED8]">（必須）</span>
              </label>
              <input
                id="company"
                name="company"
                type="text"
                autoComplete="organization"
                inputMode="text"
                placeholder="例：株式会社サンプル"
                className={inputClass}
                required
              />
            </div>
            <div>
              <label
                htmlFor="name"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                お名前
                <span className="text-[#1D4ED8]">（必須）</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                inputMode="text"
                placeholder="例：山田太郎"
                className={inputClass}
                required
              />
            </div>
            <div>
              <label
                htmlFor="email"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                メールアドレス
                <span className="text-[#1D4ED8]">（必須）</span>
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                placeholder="例：xxxx@gmail.com"
                className={inputClass}
                required
              />
            </div>
            <div>
              <label
                htmlFor="phone"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                電話番号<span className="font-normal text-[#52525B]">（任意）</span>
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
                htmlFor="vehicle_scale"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                車両台数目安<span className="font-normal text-[#52525B]">（任意）</span>
              </label>
              <select id="vehicle_scale" name="vehicle_scale" className={selectClass}>
                <option value="">選択してください</option>
                <option>未定・相談したい</option>
                <option>〜10台</option>
                <option>11〜30台</option>
                <option>31〜60台</option>
                <option>61台〜</option>
              </select>
            </div>
            <div>
              <label
                htmlFor="preferred_format"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                希望する実施形態<span className="font-normal text-[#52525B]">（任意）</span>
              </label>
              <select
                id="preferred_format"
                name="preferred_format"
                className={selectClass}
              >
                <option value="">選択してください</option>
                <option>未定</option>
                <option>集合中心</option>
                <option>オンライン中心</option>
                <option>ハイブリッド</option>
              </select>
            </div>
            <div>
              <label
                htmlFor="message"
                className="text-left text-sm font-semibold text-[#18181B]"
              >
                お問い合わせ内容
                <span className="text-[#1D4ED8]">（必須）</span>
              </label>
              <textarea
                id="message"
                name="message"
                inputMode="text"
                placeholder="例：来月から四半期ごとの安全研修を再設計したい／朝礼で使える短いネタも欲しい"
                className={textareaClass}
                required
              />
            </div>
            <div className="border border-[#E4E4E7] bg-[#FAFAF9] p-4">
              <div className="flex gap-3">
                <input
                  id="privacy_agree"
                  name="privacy_agree"
                  type="checkbox"
                  className="mt-1 h-5 w-5 shrink-0 border border-[#E4E4E7] text-[#1D4ED8] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB]"
                  required
                />
                <label
                  htmlFor="privacy_agree"
                  className="text-left text-sm leading-relaxed text-[#18181B]"
                >
                  個人情報の取り扱いに同意する
                  <span className="text-[#1D4ED8]">（必須）</span>
                </label>
              </div>
            </div>

            {error ? (
              <p className="text-left text-sm text-[#18181B]" role="alert">
                送信できませんでした。通信状況をご確認のうえ、もう一度お試しください。
                <span className="mt-1 block text-[#52525B]">{error}</span>
              </p>
            ) : null}

            <button
              type="submit"
              className={`${ctaButtonClass()} flex w-full items-center justify-center gap-2 sm:min-h-[52px]`}
            >
              <Send className="h-5 w-5 shrink-0" aria-hidden />
              内容を送信する
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
