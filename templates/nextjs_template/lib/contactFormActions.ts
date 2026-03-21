"use server";

export type ContactFormState =
  | { ok: true; message: string }
  | { ok: false; message: string; fieldErrors?: Record<string, string> };

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRe = /^[\d\-+() ]{10,20}$/;

export async function submitContactForm(
  _prev: ContactFormState | undefined,
  formData: FormData,
): Promise<ContactFormState> {
  const company = String(formData.get("company") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const phone = String(formData.get("phone") ?? "").trim();
  const topic = String(formData.get("topic") ?? "").trim();
  const message = String(formData.get("message") ?? "").trim();
  const consent = formData.get("consent") === "on";

  const fieldErrors: Record<string, string> = {};

  if (!company) fieldErrors.company = "必須項目が未入力です。";
  if (!name) fieldErrors.name = "必須項目が未入力です。";
  if (!email) fieldErrors.email = "必須項目が未入力です。";
  else if (!emailRe.test(email))
    fieldErrors.email = "メールアドレスの形式をご確認ください。";
  if (phone && !phoneRe.test(phone.replace(/\s/g, "")))
    fieldErrors.phone = "電話番号の形式をご確認ください。";
  if (!topic) fieldErrors.topic = "必須項目が未入力です。";
  if (!message) fieldErrors.message = "必須項目が未入力です。";
  if (!consent) fieldErrors.consent = "同意が必要です。";

  if (Object.keys(fieldErrors).length > 0) {
    return {
      ok: false,
      message: "送信前に入力内容をご確認ください。",
      fieldErrors,
    };
  }

  return {
    ok: true,
    message:
      "送信ありがとうございました。内容を確認のうえ、ご連絡します。",
  };
}
