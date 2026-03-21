import { ArrowRight, ClipboardList, RefreshCw, Search } from "lucide-react";
import CtaButton from "@/components/CtaButton";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionY = "py-16 md:py-20";

export default function FeaturesPage() {
  return (
    <div className="w-full">
      <section className="border-b border-[#e7e5e4] bg-[#ffffff]">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="grid items-start gap-10 py-16 md:grid-cols-2 md:py-20">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-[#0f172a] md:text-4xl">
                提供の特徴
              </h1>
              <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
                「話を聞いただけでは変わらない」を前提に、対話と可視化で改善に繋げるための設計を説明します（図解は実装でマークアップ化）。
              </p>
            </div>
            <div className="w-full max-w-full">
              <ImagePlaceholder
                aspectClassName="aspect-video"
                overlayText="対話と評価の見方をつなぐ概念図（実装マークアップ）"
                description="16:9。シンプルな矢印フロー図の代わりに置くプレースホルダ。落ち着いたティールアクセントの線画イメージ。"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            正解を並べる前に、現場の言葉で整理する
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            講義で結論だけ渡すのではなく、同席者が持ち寄る具体（個人が特定されない形）を材料に、気づきを言語化します。管理者の方が社内で再説明しやすいよう、「なぜそう言えるのか」の筋道を一緒に作ります。
          </p>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#ffffff]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            点数と理由のイメージで、次の一手が決まる
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            GPS等を用いた評価は、ドライバーを責めるための道具ではなく、習慣化の手がかりとして扱います。
            <br />
            <br />
            たとえば次のようなイメージを共有します（数値や基準の詳細は契約・実装条件に応じて調整）。
          </p>
          <ul className="mt-8 space-y-4">
            {[
              {
                title: "見える化",
                body: "急加減速、カーブ手前の速度、停車の仕方など、一般道で再現しやすい行動に焦点",
              },
              {
                title: "説明可能性",
                body: "減点や注意の理由を、ドライバーが自分の運転と結びつけられる言葉にする",
              },
              {
                title: "改善サイクル",
                body: "振り返り→優先課題→再確認→次の目標",
              },
            ].map((item) => (
              <li
                key={item.title}
                className="border border-[#e7e5e4] bg-[#fafaf9] p-6"
              >
                <p className="font-semibold text-[#0f172a]">{item.title}</p>
                <p className="mt-2 text-left text-base leading-[1.7] text-[#57534e]">
                  {item.body}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            良い教材でも、現場に戻ると薄まることがある
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            外部の講話や教材は有用ですが、社内では「自分の運転は別」と分離されやすいことがあります。当サービスは、貴社の運用に合わせた対話と、評価の見方の共有によって、日常の運転に接続することを重視します。
          </p>
        </div>
      </section>

      <section className={`${sectionY} border-b border-[#e7e5e4] bg-[#ffffff]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            実施の流れ（概念図の説明文）
          </h2>
          <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                step: "1",
                label: "現状の言語化（対話）",
                Icon: Search,
              },
              {
                step: "2",
                label: "評価の見方の合意（誤解の解消）",
                Icon: ClipboardList,
              },
              {
                step: "3",
                label: "優先改善ポイントの決定",
                Icon: ArrowRight,
              },
              {
                step: "4",
                label: "朝礼・現場での継続の型",
                Icon: RefreshCw,
              },
            ].map((item, idx, arr) => (
              <div key={item.step} className="relative">
                <div className="flex h-full flex-col border border-[#e7e5e4] bg-[#fafaf9] p-6">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-none border border-[#e7e5e4] bg-[#ffffff] text-sm font-bold text-[#0f766e]">
                      {item.step}
                    </span>
                    <item.Icon className="h-6 w-6 text-[#0f766e]" aria-hidden />
                  </div>
                  <p className="mt-4 text-left text-base font-semibold leading-snug text-[#0f172a]">
                    {item.label}
                  </p>
                </div>
                {idx < arr.length - 1 ? (
                  <div
                    className="absolute right-[-12px] top-1/2 z-10 hidden -translate-y-1/2 text-[#0f766e] lg:block"
                    aria-hidden
                  >
                    <ArrowRight className="h-6 w-6" />
                  </div>
                ) : null}
              </div>
            ))}
          </div>
          <div className="mt-10 w-full max-w-full lg:hidden">
            <p className="text-center text-sm text-[#57534e]">
              スマートフォンでは上から順に進む流れで表示しています。
            </p>
          </div>
        </div>
      </section>

      <section className={`${sectionY} bg-[#fafaf9]`}>
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2 className="text-xl font-semibold text-[#0f172a] md:text-2xl">
            社内説明用に、資料化も支援します
          </h2>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <CtaButton href={BOOKING_URL}>相談予約</CtaButton>
            <CtaButton href="/contact">要件を送る</CtaButton>
          </div>
        </div>
      </section>
    </div>
  );
}
