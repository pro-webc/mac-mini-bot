import CtaButton from "@/components/CtaButton";
import LinePlaceholderLink from "@/components/LinePlaceholderLink";

import PageHeaderWithVisual from "./PageHeaderWithVisual";

const sectionY = "py-16 md:py-24";

export default function ProgramPage() {
  return (
    <>
      <PageHeaderWithVisual
        title="プログラム／期間"
        lead="実践定着を見据えた設計です。期間は目安であり、組織の状況に応じて調整します。"
        visualDescription="横長。カレンダーではなく「伴走」「振り返り」「実践」のリズムを示すタイムライン用の余白。落ち着いたタイポ中心。写真トーンはダーク基調に馴染むグレースケール想定。"
        visualOverlay="プログラム／伴走設計"
        aspectClassName="aspect-[4/3] md:aspect-[21/9]"
      />

      <section className={sectionY} aria-labelledby="prog-duration-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="prog-duration-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            トレーニング期間：おおむね4.5〜6ヶ月
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            集合研修やワークの密度、宿題・実践課題の設計により前後します。現場への定着を重視し、伴走のイメージとして最大でおおむね1年スパンで見るケースもあります。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="prog-flow-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="prog-flow-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            一度きりの刺激では終わらせない
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            気づきを言語化し、行動に翻訳し、振り返りを繰り返すサイクルを組み込みます。オンラインで全国対応し、参加者の負荷と事業サイクルの両方に配慮します。
          </p>

          <div
            className="mt-10 grid gap-4 md:grid-cols-3"
            aria-label="進行サイクル（図解）"
          >
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                Step 1
              </p>
              <p className="mt-2 text-base font-semibold text-[#eceff4]">
                気づきの言語化
              </p>
              <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                内省を言葉にし、再現可能な表現へ整えます。
              </p>
            </div>
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                Step 2
              </p>
              <p className="mt-2 text-base font-semibold text-[#eceff4]">
                行動への翻訳
              </p>
              <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                翌週の会議・評価・意思決定に接続します。
              </p>
            </div>
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <p className="text-xs font-semibold tracking-wide text-[#94a3b8]">
                Step 3
              </p>
              <p className="mt-2 text-base font-semibold text-[#eceff4]">
                振り返りの反復
              </p>
              <p className="mt-2 text-sm leading-[1.7] text-[#94a3b8]">
                定着を見ながら、設計を微調整します。
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className={sectionY} aria-labelledby="prog-commit-heading">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="prog-commit-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            人の変容と、事業への効果
          </h2>
          <p className="mt-6 max-w-prose text-base leading-[1.7] text-[#94a3b8]">
            人への思い・期待・愛を軸にしつつ、事業における効果については定量的な観点も含めてコミットメントする方針です。ただし、指標や測定設計は案件ごとに合意のうえで設計します。
          </p>
        </div>
      </section>

      <section
        className={`${sectionY} border-y border-[#334155] bg-[#1f2937]/40`}
        aria-labelledby="prog-faq-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <h2
            id="prog-faq-heading"
            className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
          >
            よくある質問
          </h2>
          <div className="mt-8 space-y-6">
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <h3 className="text-lg font-semibold text-[#eceff4]">
                オンラインでも十分ですか。
              </h3>
              <p className="mt-3 text-base leading-[1.7] text-[#94a3b8]">
                はい。対話と演習を中心に、画面越しでも深い内省と言語化が進むよう設計します。
              </p>
            </div>
            <div className="rounded-[14px] border border-[#334155] bg-[#111827] p-6">
              <h3 className="text-lg font-semibold text-[#eceff4]">
                部門横断で実施できますか。
              </h3>
              <p className="mt-3 text-base leading-[1.7] text-[#94a3b8]">
                可能です。評価制度や会議体の違いを踏まえ、衝突が起きにくい進行に調整します。
              </p>
            </div>
          </div>
        </div>
      </section>

      <section
        className={`${sectionY} border-t border-[#334155]`}
        aria-labelledby="prog-cta-heading"
      >
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="rounded-[14px] border border-[#334155] bg-[#1f2937] p-8 md:p-12">
            <h2
              id="prog-cta-heading"
              className="text-2xl font-semibold tracking-tight text-[#eceff4] md:text-3xl"
            >
              貴社の文脈に合わせた設計をご提案します
            </h2>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <CtaButton href="/contact">相談する（フォーム）</CtaButton>
              <LinePlaceholderLink className="justify-center sm:justify-start">
                LINEで更新を受け取る
              </LinePlaceholderLink>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
