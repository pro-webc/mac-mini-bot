import { ChevronRight, Mail } from "lucide-react";
import CtaButton from "@/components/CtaButton";

type ContactCtaSectionProps = {
  variant?: "default" | "services" | "works" | "company" | "recruit" | "process" | "blog";
};

const copy: Record<
  NonNullable<ContactCtaSectionProps["variant"]>,
  { title: string; body: string }
> = {
  default: {
    title: "まずはお気軽にご相談ください",
    body: "ご不明点や現地の状況がまだ固まっていなくても大丈夫です。希望の連絡手段・時間帯があればフォームにご記入ください。",
  },
  services: {
    title: "サービス内容のご相談はこちら",
    body: "対応可否や目安の段取りについて、個別にヒアリングしながらご案内いたします。",
  },
  works: {
    title: "近い事例で相談したい方へ",
    body: "イメージに近い工事があるかどうか、お問い合わせでお気軽にご相談ください。",
  },
  company: {
    title: "会社情報・打ち合わせのご希望",
    body: "正式表記や所在地の更新は随時行います。訪問前に知りたいことがあれば、先にメッセージでお送りいただいても構いません。",
  },
  recruit: {
    title: "採用のご相談",
    body: "採用は親会社採用サイトを主軸にご案内しています。当サイトからの問い合わせも可能です。",
  },
  process: {
    title: "お問い合わせフォームが最優先の窓口です",
    body: "流れやFAQを読んだうえで、具体的な状況をフォームからお送りください。急ぎの場合は電話もご利用ください。",
  },
  blog: {
    title: "記事を読んだうえで、具体的に相談したい方へ",
    body: "お問い合わせフォームが最優先の窓口です。設備種別が未確定でも、ヒアリングから整理できます。",
  },
};

export default function ContactCtaSection({
  variant = "default",
}: ContactCtaSectionProps) {
  const { title, body } = copy[variant];

  return (
    <section className="border-t border-white/15 bg-[#1d4ed8] px-4 py-16 md:px-6">
      <div className="mx-auto max-w-6xl text-center">
        <h2 className="text-2xl font-bold tracking-tight text-white md:text-3xl">{title}</h2>
        <p className="mx-auto mt-4 max-w-2xl text-left text-base leading-relaxed text-[#E0F2FE] md:text-center">
          {body}
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <CtaButton href="/contact">
            <span className="inline-flex items-center gap-2">
              <Mail className="h-5 w-5" aria-hidden />
              お問い合わせフォームへ
              <ChevronRight className="h-5 w-5" aria-hidden />
            </span>
          </CtaButton>
          <a
            href="tel:0669745788"
            className="inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-full border-2 border-white bg-[#1d4ed8] px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-[#1e40af] active:bg-[#1e3a8a] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
          >
            06-6974-5788
          </a>
        </div>
      </div>
    </section>
  );
}
