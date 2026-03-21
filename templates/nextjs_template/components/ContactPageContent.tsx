import CtaButton from "@/components/CtaButton";
import ContactFormBlock from "@/components/ContactFormBlock";
import ImagePlaceholder from "@/components/ImagePlaceholder";
import { BOOKING_URL } from "@/lib/bookingUrl";

const sectionPad = "border-b border-[#e7e5e4] py-16 md:py-20";
const inner = "mx-auto max-w-6xl px-4 md:px-6";

export default function ContactPageContent() {
  return (
    <>
      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h1 className="text-2xl font-bold tracking-tight text-[#0f172a] sm:text-3xl md:text-4xl">
            お問い合わせ・相談予約
          </h1>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e] sm:text-lg">
            ご相談は、まずオンライン面談の予約からでも、フォームからでも進められます。社内稟議用に必要な資料の有無や、希望の連絡手段もお知らせください。
          </p>
          <div className="mt-10">
            <ImagePlaceholder
              aspectClassName="aspect-video"
              overlayText="オンライン面談・フォームの二本立て導線"
              description="横長・ノートPCの画面にカレンダーUIが写り、横にメモとペン。人物の手元のみ。明るいデスク、落ち着いた色調。過度なストック写真感を避ける。"
            />
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="sr-only">返信目安</h2>
          <p className="max-w-prose text-left text-base font-semibold text-[#0f172a]">
            3営業日以内にご返信いたします。
          </p>
          <p className="mt-2 max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            繁忙期は順延する場合があります。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            面談を予約する
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            別途アカウント取得が必要な外部予約ツールを利用します。画面の案内にしたがって日時を選択し、必要事項を入力してください。予約完了後に受信する確認メールを保存しておくと、社内共有がスムーズです。
          </p>
          <div className="mt-8">
            <CtaButton href={BOOKING_URL}>面談を予約する</CtaButton>
          </div>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            メールでのお問い合わせ
          </h2>
          <ContactFormBlock />
        </div>
      </section>

      <section className={`${sectionPad} bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            電話・メールでの連絡（方針）
          </h2>
          <p className="mt-6 max-w-prose text-left text-base leading-[1.7] text-[#57534e]">
            公開する電話番号・メールアドレスは、運営情報としてサイトの該当箇所に明示します。フォームが最優先の導線ですが、急ぎのご用件は電話での受付方法を併記します（番号は確定後に掲載）。
          </p>
        </div>
      </section>

      <section className={`${sectionPad} bg-[#fafaf9]`}>
        <div className={inner}>
          <h2 className="text-xl font-bold text-[#0f172a] sm:text-2xl md:text-3xl">
            よくあるご質問（手続き）
          </h2>
          <dl className="mt-8 space-y-8">
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                見積り前に社内説明したいです。
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                可能です。フォームに「社内説明用に欲しい要点」を書いてください。箇条書きの要約や、当日の進行イメージを返信に含めます。
              </dd>
            </div>
            <div className="border border-[#e7e5e4] bg-[#ffffff] p-6">
              <dt className="text-lg font-bold text-[#0f172a]">
                予約ツールで日程が合いません。
              </dt>
              <dd className="mt-3 text-left text-base leading-[1.7] text-[#57534e]">
                フォームに希望候補日を複数ご記載ください。こちらから調整案を返信します。
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <section className={`${sectionPad} border-b-0 bg-[#ffffff]`}>
        <div className={inner}>
          <h2 className="sr-only">免責・運営注意</h2>
          <p className="max-w-prose text-left text-sm leading-[1.7] text-[#57534e]">
            本サイトの情報は、掲載時点の一般的な説明を目的としたものです。実施内容・条件・費用は、個別のお打ち合わせと合意内容を優先します。
          </p>
        </div>
      </section>
    </>
  );
}
